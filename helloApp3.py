import flask
import requests
import json
import time
from flask import make_response
from flask import send_from_directory, request

data = {   "grant_type": "refresh_token",
           "client_id": "CLIENT ID",
           "refresh_token": "User Key" }

headers = { "Content-Type" : "application/json",
            "X-UIPATH-TenantName" : "TenantName" }

r0 = requests.post("https://account.uipath.com/oauth/token", data, headers)
response0 = json.loads(r0.content)

auth = "Bearer "+response0["access_token"]

headers1 = { "Content-Type" : "application/json",
             "X-UIPATH-TenantName" : "TenantName",
             "Authorization" : auth}

r1 = requests.get("https://cloud.uipath.com/OrganizationID/TenantName/odata/Folders?$Filter=DisplayName eq 'OrchestratorFolderName'", headers =headers1)
response1 = json.loads(r1.text)

orgID = str(response1["value"][0]["Id"])

headers2 = { "Content-Type" : "application/json",
             "X-UIPATH-TenantName" : "TenantName",
             "X-UIPATH-OrganizationUnitId" : orgID,
             "Authorization" : auth}

r2 = requests.get("https://cloud.uipath.com/OrganizationID/TenantName/odata/Releases?$filter=Name eq 'ProcessName'", headers =headers2)
response2 = json.loads(r2.text)

releaseKey = response2["value"][0]["Key"]

app = flask.Flask(__name__)

@app.route('/uiRobot', methods=['POST'])

def uiRobot():
    req = request.get_json(silent=True, force= True)
  
    intentName = req["queryResult"]["intent"]["displayName"]
    
    if intentName == "GetResults":
        country = req["queryResult"]["parameters"]["Country"]
        gender = req["queryResult"]["parameters"]["Gender"]
        nameset = req["queryResult"]["parameters"]["Name-Set"]
        startInfo = {}
        startInfo['ReleaseKey'] = releaseKey
        startInfo['Strategy'] = 'ModernJobsCount'
        startInfo['JobsCount'] = '1'
        startInfo['InputArguments'] = json.dumps({"in_Sexe":gender,"in_Pays":country,"in_EnsembleMots":nameset})                     

        data2 ={}
        data2['startInfo'] = startInfo
        json_data = json.dumps(data2)
        
        r2 = requests.post("https://cloud.uipath.com/OrganizationID/TenantName/odata/Jobs/UiPath.Server.Configuration.OData.StartJobs", data = json_data, headers = headers2)
        wjdata2= json.loads(r2.text)
        time.sleep(4)
        return ""

    if intentName == "DisplayResults":
        r3 = requests.get("https://cloud.uipath.com/OrganizationID/TenantName/odata/Jobs?$Filter=State eq 'Successful' AND ReleaseName eq 'ProcessName'&$orderby=EndTime DESC", headers = headers2)
        wjdata2 = json.loads(r3.text)
        result1 = wjdata2["value"][0]["OutputArguments"]
        result2= json.loads(result1)
        res1 = result2['out_ExtractedName']
        res2 = result2['out_ExtractedAdresse']
  
        r = json.dumps({
        'fulfillmentText': str("Your fake name and address are: "+ res1+", ")+res2,
        })
        return r
    
if __name__ == "__main__":
    app.secret_key = 'ItIsASecret'
    app.debug = True
    app.run()