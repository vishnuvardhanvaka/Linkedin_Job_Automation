import time
from fastapi import FastAPI
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

@app.post('/job_automate')
async def job_automate(data:JobAutomate):
    try:
        print(data.email,data.password)
        cookies = {
            'li_at': 'AQEDATT2JCEC5HMOAAABkTeI5DcAAAGRgyMA8k4AqBQ_Noi0Srmy4I74twvvYwYuXV4xrLXlgDGHl9DbBXGsmCTaZG8gTnfvcl51bZZuh7Rr1ZbPPHL3-PehwskadvBK4PTphY0m75ekXET1gTbxrBZi',
            'JSESSIONID': "ajax:4194401157081035938",
        }
        no_of_jobs_to_apply=1
        start = time.time()
        appliedData=Linkedin(data.email,data.password,no_of_jobs_to_apply).linkJobApply()
        print(appliedData)
        return {'status':True,"appliedData":appliedData}
    except Exception as e:
        app.utils.prRed("Error in main: " +str(e))
        # close firefox driver
        end = time.time()
        app.utils.prYellow("---Took: " + str(round((time.time() - start)/60)) + " minute(s).")
        Linkedin().driver.quit()
        return {'status':False}


