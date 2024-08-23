import json,ast
import time
import app.utils as utils
from fastapi import FastAPI,BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from app.declarations import JobAutomate
from app.bot import Linkedin

origins=['*']
app=FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def clean_json_string(json_string):
    json_string = json_string.replace("'", '"')
    json_string = json_string.replace('"\"', '"')  # Fix escaped quotes
    json_string = json_string.replace('\""', '"')  # Fix escaped quotes
    json_string = json_string.replace('""', '"')
    json_string = json_string.replace('"{', '{')
    json_string = json_string.replace('}"', '}')
    json_string = json_string.rstrip(',')  # Remove any trailing commas
    return json_string

def getLoginCookies(cookie_string):
    JSESSIONID=None
    li_at=None
    # try:
    cleaned_cookie_string=clean_json_string(cookie_string)
    cookies=ast.literal_eval(cleaned_cookie_string)
    for cookie in cookies:
        if cookie['name']=='JSESSIONID':
            JSESSIONID=cookie['value']
        if cookie['name']=='li_at':
            li_at=cookie['value']
        
    # except Exception as e:
    #     print(e)
    return {'JSESSIONID':JSESSIONID,'li_at':li_at}
    

@app.post('/linkedin-automate/job_automate')
async def job_automate(data:JobAutomate,background_tasks: BackgroundTasks):
    try:
        start=time.time()
        login_cookies = getLoginCookies(f'''{data.cookie_string}''')
        no_of_jobs_to_apply = 1
        Linkedin_driver = Linkedin(no_of_jobs_to_apply)
        checkEmail = Linkedin_driver.login_with_cookies(login_cookies)
        
        if checkEmail:
            background_tasks.add_task(Linkedin_driver.linkJobApply)
            return {'status': True, 'msg': 'Jobs applying has started in background!'}
        else:
            Linkedin_driver.driver.quit()
            return {'status': False, 'msg': 'Invalid cookie. Login Failed!'}
    except Exception as e:
        utils.prRed("Error in main: " +str(e))
        # close firefox driver
        end = time.time()
        utils.prYellow("---Took: " + str(round((time.time() - start)/60)) + " minute(s).")
        # Linkedin().driver.quit()
        return {'status': False, 'msg': str(e)}


