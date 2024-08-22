import json,ast
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
    

@app.post('/job_automate')
async def job_automate(data:JobAutomate):
    try:
        # cookie_string='''[{"domain":".linkedin.com","hostOnly":false,"httpOnly":false,"name":"lang","path":"/","sameSite":"no_restriction","secure":true,"session":true,"storeId":"0","value":"v=2&lang=en-us"},{"domain":".linkedin.com","expirationDate":1755849904.42411,"hostOnly":false,"httpOnly":false,"name":"bcookie","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"0","value":"\"v=2&288b6ff1-f6d7-4493-87aa-da64930326e8\""},{"domain":".www.linkedin.com","expirationDate":1755849902.30581,"hostOnly":false,"httpOnly":true,"name":"bscookie","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"0","value":"\"v=1&2024062809104719ce9784-9266-4da1-8b9d-bbc3c30dd5bfAQFHXQkrxjKrfczRYdb1XTB02NThhrCq\""},{"domain":".linkedin.com","expirationDate":1732089903.423882,"hostOnly":false,"httpOnly":false,"name":"li_sugr","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"0","value":"ff82c172-650a-4301-b0ce-aa4e900242a5"},{"domain":"www.linkedin.com","expirationDate":1736512110,"hostOnly":true,"httpOnly":false,"name":"g_state","path":"/","sameSite":"unspecified","secure":false,"session":false,"storeId":"0","value":"{\"i_l\":0}"},{"domain":".linkedin.com","expirationDate":1755413198.407789,"hostOnly":false,"httpOnly":false,"name":"liap","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"0","value":"true"},{"domain":".www.linkedin.com","expirationDate":1755413198.407953,"hostOnly":false,"httpOnly":false,"name":"JSESSIONID","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"0","value":"\"ajax:4194401157081035938\""},{"domain":".www.linkedin.com","expirationDate":1739865900,"hostOnly":false,"httpOnly":false,"name":"li_theme","path":"/","sameSite":"unspecified","secure":true,"session":false,"storeId":"0","value":"light"},{"domain":".www.linkedin.com","expirationDate":1739865900,"hostOnly":false,"httpOnly":false,"name":"li_theme_set","path":"/","sameSite":"unspecified","secure":true,"session":false,"storeId":"0","value":"app"},{"domain":"www.linkedin.com","hostOnly":true,"httpOnly":true,"name":"PLAY_SESSION","path":"/","sameSite":"lax","secure":true,"session":true,"storeId":"0","value":"eyJhbGciOiJIUzI1NiJ9.eyJkYXRhIjp7ImZsb3dUcmFja2luZ0lkIjoiL1NzdU8rQUdTRnV6dVRjeVFmdVR4Zz09In0sIm5iZiI6MTcyMzIxMzU5NSwiaWF0IjoxNzIzMjEzNTk1fQ.JPffuFBTWDmzxV0-FUA_HCO1SyVgSxXiDsDjhFjrmlg"},{"domain":".linkedin.com","hostOnly":false,"httpOnly":false,"name":"AMCVS_14215E3D5995C57C0A495C55%40AdobeOrg","path":"/","sameSite":"unspecified","secure":false,"session":true,"storeId":"0","value":"1"},{"domain":".linkedin.com","expirationDate":1726905903,"hostOnly":false,"httpOnly":false,"name":"aam_uuid","path":"/","sameSite":"unspecified","secure":false,"session":false,"storeId":"0","value":"70471809808464155201395641237898003334"},{"domain":".linkedin.com","expirationDate":1754828415.022975,"hostOnly":false,"httpOnly":true,"name":"dfpfpt","path":"/","sameSite":"lax","secure":true,"session":false,"storeId":"0","value":"120d679fe27843a2bc4caa9102878fb2"},{"domain":".www.linkedin.com","expirationDate":1755413198.407683,"hostOnly":false,"httpOnly":true,"name":"li_at","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"0","value":"AQEDATT2JCEC5HMOAAABkTeI5DcAAAGRgyMA8k4AqBQ_Noi0Srmy4I74twvvYwYuXV4xrLXlgDGHl9DbBXGsmCTaZG8gTnfvcl51bZZuh7Rr1ZbPPHL3-PehwskadvBK4PTphY0m75ekXET1gTbxrBZi"},{"domain":".www.linkedin.com","expirationDate":1725523500,"hostOnly":false,"httpOnly":false,"name":"timezone","path":"/","sameSite":"unspecified","secure":true,"session":false,"storeId":"0","value":"Asia/Calcutta"},{"domain":".linkedin.com","expirationDate":1726754020.223204,"hostOnly":false,"httpOnly":false,"name":"AnalyticsSyncHistory","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"0","value":"AQKaX20d5pQERwAAAZFwEJK3fVxkHzuBGCaUIXmZV2kS7GXLaaKWA4OUdY2ImaKfNlZMceA-TLtj3IjsN1wJXg"},{"domain":".linkedin.com","expirationDate":1731938020.789946,"hostOnly":false,"httpOnly":false,"name":"_guid","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"0","value":"b2cf9042-d23d-4505-9e2f-cd2b67110bcd"},{"domain":".linkedin.com","expirationDate":1726754020.792821,"hostOnly":false,"httpOnly":false,"name":"lms_ads","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"0","value":"AQE_PfHr9Ei-kgAAAZFwEJT52__oOTj1nxZpBfdhqT7vvsly9NNlwaq-h-amocx1t409jizmYhsJVB7q3dTCxHWmA-vqHGJX"},{"domain":".linkedin.com","expirationDate":1726754020.792967,"hostOnly":false,"httpOnly":false,"name":"lms_analytics","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"0","value":"AQE_PfHr9Ei-kgAAAZFwEJT52__oOTj1nxZpBfdhqT7vvsly9NNlwaq-h-amocx1t409jizmYhsJVB7q3dTCxHWmA-vqHGJX"},{"domain":".linkedin.com","expirationDate":1731945403,"hostOnly":false,"httpOnly":false,"name":"_gcl_au","path":"/","sameSite":"unspecified","secure":false,"session":false,"storeId":"0","value":"1.1.374745387.1724162037"},{"domain":".linkedin.com","expirationDate":1739859069,"hostOnly":false,"httpOnly":false,"name":"AMCV_14215E3D5995C57C0A495C55%40AdobeOrg","path":"/","sameSite":"unspecified","secure":false,"session":false,"storeId":"0","value":"-637568504%7CMCIDTS%7C19958%7CMCMID%7C69906278550937101871410048290346430541%7CMCAAMLH-1724911869%7C12%7CMCAAMB-1724911869%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1724314269s%7CNONE%7CMCCIDH%7C-190029254%7CvVersion%7C5.1.1"},{"domain":".linkedin.com","hostOnly":false,"httpOnly":true,"name":"fptctx2","path":"/","sameSite":"lax","secure":true,"session":true,"storeId":"0","value":"taBcrIH61PuCVH7eNCyH0MJojnuUODHcZ6x9WoxhgCmAUSGhA5IZk%252bqZR8%252f%252fh1gRPbMkXj0qwxoMWjwUmueJYYZxcLU3yAWB493H%252fJRlRHDxaScpmF90r4c%252f6OpHnEWor95jixnkuxsgIUGcyPGXR6oFiWkJqJWvPHTpXBa1SJm43QqzNRs%252bQ%252fMiUpVUvOpFD8WB2DDZpIXbc3x96bt4MCKeefYt%252bTjWcIJaN6kUOTXL4vM%252balFCdwfPlGJEkKi0Y4gC4m4%252bV%252fSSg%252bS8mcqzGUaQnL3t66CBc1Wmkt8grsGzxFuQm2dozr4O3oLpybb3Jl39NnKMcB3mYXTMaK9V0%252f84%252fFmwJbSqC470rVuBjac%253d"},{"domain":".linkedin.com","hostOnly":false,"httpOnly":false,"name":"sdsc","path":"/","sameSite":"no_restriction","secure":true,"session":true,"storeId":"0","value":"22%3A1%2C1724313362569%7EJAPP%2C0K6qh3jW6hkvODE%2Fx3eANH7IpidU%3D"},{"domain":".linkedin.com","expirationDate":1726905902,"hostOnly":false,"httpOnly":false,"name":"UserMatchHistory","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"0","value":"AQLEcBijmCpxbQAAAZF5HhZ98eBER9gLwseRRnunSLqorMOD8jvckXweEeaSjv6t4qJ7PvSE5d6m-RavBZaTGaR2JD4eqrbte0eax3_6VpIyC-CEN8hp8ra2AKCVUL9kDjPmBeYoGXmScmFb0mgHcJjwSmCXjP2iMZ2VIjuAsfnVlcZAiO_V1CsL2Cc2ZimOZOuaxjbAmSSxX2v_BmGs8ODgiPeszL7pC_VHo6r1Jw4wKV_XE0n0Ne9NHYZDE3evqeCsQWL1hX2fV0qCXxe4yEBcy65BMObEdrEbloBh9IaEdrefSs7gmidhdRD4ji2R26IodFvEdhddqQy_7nY4Eg63E4BCv37TKbyqRhzOoIHuKcVyiw"},{"domain":".linkedin.com","expirationDate":1724344776.217575,"hostOnly":false,"httpOnly":false,"name":"lidc","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"0","value":"\"b=OB37:s=O:r=O:a=O:p=O:g=4654:u=568:x=1:i=1724315340:t=1724344775:v=2:sig=AQH69LcNbhbBuJBJBPgPhZz1zy4MVVh7\""}]'''
        # login_cookies = {
        #     'li_at': 'AQEDATT2JCEC5HMOAAABkTeI5DcAAAGRgyMA8k4AqBQ_Noi0Srmy4I74twvvYwYuXV4xrLXlgDGHl9DbBXGsmCTaZG8gTnfvcl51bZZuh7Rr1ZbPPHL3-PehwskadvBK4PTphY0m75ekXET1gTbxrBZi',
        #     'JSESSIONID': "ajax:4194401157081035938",
        # }
        # JSESSIONID,li_at="ajax:4194401157081035938",'AQEDATT2JCEC5HMOAAABkTeI5DcAAAGRgyMA8k4AqBQ_Noi0Srmy4I74twvvYwYuXV4xrLXlgDGHl9DbBXGsmCTaZG8gTnfvcl51bZZuh7Rr1ZbPPHL3-PehwskadvBK4PTphY0m75ekXET1gTbxrBZi'
        
        login_cookies=getLoginCookies(f'''{data.cookie_string}''')
        no_of_jobs_to_apply=1
        start = time.time()
        appliedData=Linkedin(login_cookies,no_of_jobs_to_apply).linkJobApply()
        print(appliedData)
        return {'status':True,"appliedData":appliedData}
    except Exception as e:
        app.utils.prRed("Error in main: " +str(e))
        # close firefox driver
        end = time.time()
        app.utils.prYellow("---Took: " + str(round((time.time() - start)/60)) + " minute(s).")
        Linkedin().driver.quit()
        return {'status':False}


