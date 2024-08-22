import math
import os
import random
import app.config,app.utils,app.constants
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Linkedin:
    def __init__(self,no_of_jobs_to_apply):
        chrome_driver_path = './chromedriver-win64/chromedriver.exe'
        chrome_options = Options()
        WINDOW_SIZE = "1920,1080"
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
        chrome_options.add_argument("--log-level=1")
        
        # chrome_options.binary_location = CHROME_PATH

        service = Service(executable_path=chrome_driver_path)
        # self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.logged=False
        self.driver = webdriver.Chrome(options=chrome_options)

        self.no_of_jobs_to_apply=no_of_jobs_to_apply
        # self.login_with_cookies(login_cookies)

    #login
    def login_with_cookies(self, cookies):
        self.driver.get("https://www.linkedin.com/")
        app.utils.prYellow("Logging in with cookies.")
        try:
            for cookie_name, cookie_value in cookies.items():
                self.driver.add_cookie({'name': cookie_name, 'value': cookie_value})

            self.driver.refresh()  # Refresh the page to log in using the cookies
            time.sleep(3)  # Wait for the page to load

            # Verify login
            if "feed" in self.driver.current_url:
                app.utils.prGreen("Successfully logged in with cookies!")
                self.logged=True
                return True
            else:
                app.utils.prRed("Failed to log in with cookies.")
                return False
        except Exception as e:
            app.utils.prRed(f"An error occurred during login: {str(e)}")
            return False

    def generateUrls(self):
        if not os.path.exists('data'):
            os.makedirs('data')
        try: 
            with open('data/urlData.txt', 'w',encoding="utf-8" ) as file:
                linkedinJobLinks = app.utils.LinkedinUrlGenerate().generateUrlLinks()
                for url in linkedinJobLinks:
                    file.write(url+ "\n")
            app.utils.prGreen("Urls are created successfully, now the bot will visit those urls.")
        except:
            app.utils.prRed("Couldnt generate url, make sure you have /data folder and modified config.py file for your preferances.")

    def linkJobApply(self):
        self.generateUrls()
        countApplied = 0
        countJobs = 0
        countCannotApply=0
        appliedData={}
        if not self.logged:
            return appliedData
        urlData = app.utils.getUrlDataFile()

        for url in urlData:
            jobsApplied=0
            cannotApplyCount=0   
            alreadyAppliedCount=0

            self.driver.get(url)
            try:
                totalJobs = self.driver.find_element(By.XPATH,'//small').text 
            except:
                print("No Matching Jobs Found")
                continue
            totalPages = app.utils.jobsToPages(totalJobs)
            print(f'total jobs : {totalJobs}')
            urlWords =  app.utils.urlToKeywords(url)
            lineToWrite = "\n Category: " + urlWords[0] + ", Location: " +urlWords[1] + ", Applying " +str(totalJobs)+ " jobs."
            self.displayWriteResults(lineToWrite)

            for page in range(totalPages):
                if jobsApplied>=self.no_of_jobs_to_apply:
                    break
                print(f'current page:{page}')
                currentPageJobs = app.constants.jobsPerPage * page
                url = url +"&start="+ str(currentPageJobs)
                self.driver.get(url)
                time.sleep(random.uniform(1, app.constants.botSpeed))

                offersPerPage = self.driver.find_elements(By.XPATH,'//li[@data-occludable-job-id]')

                offerIds = []
                for offer in offersPerPage:
                    offerId = offer.get_attribute("data-occludable-job-id")
                    offerIds.append(int(offerId.split(":")[-1]))

                for jobID in offerIds:
                    print(f'jobsApplied: {jobsApplied}')
                    if jobsApplied>=self.no_of_jobs_to_apply:
                        break
                    offerPage = 'https://www.linkedin.com/jobs/view/' + str(jobID)
                    print(offerPage)
                    self.driver.get(offerPage)
                    time.sleep(random.uniform(1, app.constants.botSpeed))

                    countJobs += 1
                    jobProperties = str(jobID)#self.getJobProperties(countJobs)
                    button = self.easyApplyButton()
                    if button is not False:
                        # button.click()
                        
                        countApplied += 1
                        time.sleep(random.uniform(1, app.constants.botSpeed))
                        
                        try:
                            print('submiting')
                            self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Submit application']").click()
                            time.sleep(random.uniform(1, app.constants.botSpeed))
                            jobsApplied+=1
                            lineToWrite = jobProperties + " | " + "* 🥳 Just Applied to this job: "  +str(offerPage)
                            self.displayWriteResults(lineToWrite)

                        except:
                            try:
                                print('next direct')
                                self.driver.find_element(By.CSS_SELECTOR,"button[aria-label='Continue to next step']").click()
                                time.sleep(random.uniform(1, app.constants.botSpeed))
                                comPercentage = self.driver.find_element(By.XPATH,'html/body/div[3]/div/div/div[2]/div/div/span').text
                                percenNumber = int(comPercentage[0:comPercentage.index("%")])
                                result = self.applyProcess(percenNumber,offerPage)
                                if "Just Applied" in result:
                                        jobsApplied+=1
                                else:
                                    cannotApplyCount+=1
                                lineToWrite = jobProperties + " | " + result
                                self.displayWriteResults(lineToWrite)
                            
                            except Exception as e: 
                                try:
                                    print('country code clicking')
                                    self.driver.find_element(By.CSS_SELECTOR,"option[value='urn:li:country:" + app.config.country_code + "']").click()
                                    time.sleep(random.uniform(1, app.constants.botSpeed))
                                    print('entering phone number')
                                    self.driver.find_element(By.CSS_SELECTOR, 'input').send_keys(app.config.phone_number)
                                    time.sleep(random.uniform(1, app.constants.botSpeed))
                                    print('going to next step')
                                    self.driver.find_element(By.CSS_SELECTOR,"button[aria-label='Continue to next step']").click()
                                    time.sleep(random.uniform(1, app.constants.botSpeed))
                                    comPercentage = self.driver.find_element(By.XPATH,'html/body/div[3]/div/div/div[2]/div/div/span').text
                                    percenNumber = int(comPercentage[0:comPercentage.index("%")])
                                    result = self.applyProcess(percenNumber,offerPage)
                                    if "Just Applied" in result:
                                        jobsApplied+=1
                                    else:
                                        cannotApplyCount+=1
                                    lineToWrite = jobProperties + " | " + result
                                    self.displayWriteResults(lineToWrite)
                                except Exception as e:
                                    cannotApplyCount+=1
                                    lineToWrite = jobProperties + " | " + "* 🥵 Cannot apply to this Job! " +str(offerPage)
                                    self.displayWriteResults(lineToWrite)
                    else:
                        alreadyAppliedCount+=1
                        lineToWrite = jobProperties + " | " + "* 🥳 Already applied! Job: " +str(offerPage)
                        self.displayWriteResults(lineToWrite)


            app.utils.prYellow("Category: " + urlWords[0] + "," +urlWords[1]+ " applied: " + str(countApplied) +
                    " jobs out of " + str(countJobs) + ".")
            appliedData[urlWords[0]]={'totalJobs':totalJobs,'jobsApplied':jobsApplied,'cannotApplyCount':cannotApplyCount}
        return appliedData
            
    def getJobProperties(self, count):
        textToWrite = ""
        jobTitle = ""
        jobCompany = ""
        jobLocation = ""
        jobWOrkPlace = ""
        jobPostedDate = ""
        jobApplications = ""

        try:
            jobTitle = self.driver.find_element(By.XPATH,"//h1[contains(@class, 'job-title')]").get_attribute("innerHTML").strip()
        except Exception as e:
            app.utils.prYellow("Warning in getting jobTitle: " +str(e)[0:50])
            jobTitle = ""
        try:
            jobCompany = self.driver.find_element(By.XPATH,"//a[contains(@class, 'ember-view t-black t-normal')]").get_attribute("innerHTML").strip()
        except Exception as e:
            app.utils.prYellow("Warning in getting jobCompany: " +str(e)[0:50])
            jobCompany = ""
        try:
            jobLocation = self.driver.find_element(By.XPATH,"//span[contains(@class, 'bullet')]").get_attribute("innerHTML").strip()
        except Exception as e:
            app.utils.prYellow("Warning in getting jobLocation: " +str(e)[0:50])
            jobLocation = ""
        try:
            jobWOrkPlace = self.driver.find_element(By.XPATH,"//span[contains(@class, 'workplace-type')]").get_attribute("innerHTML").strip()
        except Exception as e:
            app.utils.prYellow("Warning in getting jobWorkPlace: " +str(e)[0:50])
            jobWOrkPlace = ""
        try:
            jobPostedDate = self.driver.find_element(By.XPATH,"//span[contains(@class, 'posted-date')]").get_attribute("innerHTML").strip()
        except Exception as e:
            app.utils.prYellow("Warning in getting jobPostedDate: " +str(e)[0:50])
            jobPostedDate = ""
        try:
            jobApplications= self.driver.find_element(By.XPATH,"//span[contains(@class, 'applicant-count')]").get_attribute("innerHTML").strip()
        except Exception as e:
            app.utils.prYellow("Warning in getting jobApplications: " +str(e)[0:50])
            jobApplications = ""

        textToWrite = str(count)+ " | " +jobTitle+  " | " +jobCompany+  " | "  +jobLocation+ " | "  +jobWOrkPlace+ " | " +jobPostedDate+ " | " +jobApplications
        return textToWrite

    def easyApplyButton(self):
        try:
            button = self.driver.find_element(By.XPATH,
                '//button[contains(@class, "jobs-apply-button")]')
            self.driver.execute_script("arguments[0].click();", button)
            EasyApplyButton = button
        except Exception as e:
            print(f"Error: {str(e)}")
            EasyApplyButton = False

        return EasyApplyButton


    def applyProcess(self, percentage, offerPage):
        applyPages = math.floor(100 / percentage) 
        result = ""  
        try:    
            for pages in range(applyPages-2):
                self.driver.find_element(By.CSS_SELECTOR,"button[aria-label='Continue to next step']").click()
                time.sleep(random.uniform(1, app.constants.botSpeed))

            self.driver.find_element(By.CSS_SELECTOR,"button[aria-label='Review your application']").click() 
            time.sleep(random.uniform(1, app.constants.botSpeed))

            if app.config.followCompanies is False:
                self.driver.find_element(By.CSS_SELECTOR,"label[for='follow-company-checkbox']").click() 
                time.sleep(random.uniform(1, app.constants.botSpeed))

            self.driver.find_element(By.CSS_SELECTOR,"button[aria-label='Submit application']").click()
            time.sleep(random.uniform(1, app.constants.botSpeed))

            result = "* 🥳 Just Applied to this job: " +str(offerPage)
        except:
            result = "* 🥵 " +str(applyPages)+ " Pages, couldn't apply to this job! Extra info needed. Link: " +str(offerPage)
        return result

    def displayWriteResults(self,lineToWrite: str):
        try:
            print(lineToWrite)
            app.utils.writeResults(lineToWrite)
        except Exception as e:
            app.utils.prRed("Error in DisplayWriteResults: " +str(e))

# start = time.time()
# try:
#     email="vishnuvardhanvaka1@gmail.com"
#     password="vishnu1$"
#     Linkedin(email,password).linkJobApply()
# except Exception as e:
#     app.utils.prRed("Error in main: " +str(e))
#     # close firefox driver
#     end = time.time()
#     app.utils.prYellow("---Took: " + str(round((time.time() - start)/60)) + " minute(s).")
#     Linkedin().driver.quit()
