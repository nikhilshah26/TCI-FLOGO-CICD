#!/usr/bin/env python
# Author : Nikhil Shah
# Date : 06/08/21
# This python script executes below CI/CD workflow which is called by jenkins..
""" We have 2 orgs we use for CI/CD in the Cooper Airlines org: Dev/QA, Staging & Pre-Production
1. The app is deployed on Dev/QA org using the flogo.json and manifest.json artifacts on github
2. Start the app and Test the endpoints
3. Copy this app from Dev/QA org to Staging  org
4. Start the new copied app in Staging org
5. Override the DB Host name app prop 
6. Retrieve the endpoints of the deployed app in Staging org
7. Invoke the endpoint to "test" it """

# How to run this code -
# python3 flogo_rest_api.py <api_url> <access_token> <sourceAppId> <subscriptionLocator> <targetSubscriptionLocator> <newAppName> <endpoint_path> <app_artifacts_github_path> <override_app_prop_json>

import json
import requests
import time
import argparse
import os

subscriptionLocator=0
targetSubscriptionLocator=''
api_url=''
Auth_Header=''

parser = argparse.ArgumentParser()
parser.add_argument('api_url')
parser.add_argument('access_token')
parser.add_argument('sourceAppId')
parser.add_argument('subscriptionLocator')
parser.add_argument('targetSubscriptionLocator')
parser.add_argument('newAppName')
parser.add_argument('endpoint_path')
parser.add_argument('app_artifacts_github_path')
parser.add_argument('override_app_prop_json')
args = parser.parse_args()

print ('api_url :',args.api_url)
print ('access_token :',args.access_token)
print ('sourceAppId :',args.sourceAppId)
print ('subscriptionLocator :',args.subscriptionLocator)
print ('targetSubscriptionLocator :',args.targetSubscriptionLocator)
print ('newAppName :',args.newAppName)
print ('endpoint_path :',args.endpoint_path)
print ('app_artifacts_github_path :',args.app_artifacts_github_path)
print ('override_app_prop_json:', args.override_app_prop_json)

api_url=args.api_url
access_token=args.access_token
sourceAppId=args.sourceAppId
subscriptionLocator=args.subscriptionLocator
targetSubscriptionLocator=args.targetSubscriptionLocator
newAppName=args.newAppName
endpoint_path=args.endpoint_path
app_artifacts_github_path=args.app_artifacts_github_path
override_app_prop_json=args.override_app_prop_json


Auth_Header={'Authorization' : 'Bearer '+access_token+'','Accept': 'application/json','User-Agent':'PostmanRuntime/7.28.3'}

#Get User Info
def get_userInfo():
    try:
        response = requests.get(api_url+'/userinfo', headers=Auth_Header)
        print('\n**** User Info*****' , response.json())  
        print ("*******",response.status_code)
    except:
        print ("Please enter valid API URL. For eg. https://api.cloud.tibco.com/tci/v1 for TCI US region.")
        exit()

def download_app_artifacts_from_githib(flogo_json_url,manifest_json_url):
    #flogo_json_url = "https://raw.githubusercontent.com/nikhilshah26/TCI-FLOGO-CICD/main/Flogo_App/flogo.json"
    #manifest_json_url= "https://raw.githubusercontent.com/nikhilshah26/TCI-FLOGO-CICD/main/Flogo_App/manifest.json"

    directory = os.getcwd()
    flogojsonfilename = directory + "/" + 'flogo.json'
    print ("flogojsonfilename="+flogojsonfilename)
    flogo_json = requests.get(flogo_json_url)

    f = open(flogojsonfilename,'w')
    f.write(flogo_json.text)
    f.close()

    #print ("****FLOGO json****",flogo_json.text)

    manifestjsonfilename = directory + "/" + 'manifest.json'
    manifest_json = requests.get(manifest_json_url)

    f1 = open(manifestjsonfilename,'w')
    f1.write(manifest_json.text)
    f1.close()

    #print ("****Manifest json****",manifest_json.text)

def pushapp_using_app_artifacts(subsLocator,appName,forceOverwrite,instanceCount,retainAppProps):
    files = [
            ('artifact', ('flogo.json', open('flogo.json', 'rb'), 'application/json')),
            ('manifest.json', ('manifest.json', open('manifest.json', 'rb'), 'application/json'))
        ]

    print("**** Deploying app with the artifacts provided******")
    response = requests.post(api_url+'/subscriptions/'+subsLocator+'/apps?appName='+appName+'&forceOverwrite='+forceOverwrite+'&instanceCount='+instanceCount+'&retainAppProps='+retainAppProps+'', headers=Auth_Header,files=files)
    time.sleep(25)
    if (response.status_code != 202):
        print ("*****Status Code****"+str(response.status_code))
        print (response.text)
        exit()
    else:
        print ("*****Status Code****"+str(response.status_code))
        print(response.json())
        resp_dict=json.loads(json.dumps(response.json()))
        appId=resp_dict['appId']
        print('\n***** App ID of deployed app ****' , appId)
        return appId


    

#Copy App
def copy_app(sourceAppId,NewAppName,subscriptionLocator,targetSubscriptionLocator):
    print ("\n*****Copying App from Dev/QA org to Staging Org******")
    if targetSubscriptionLocator != '':
        response = requests.post(api_url+'/subscriptions/'+subscriptionLocator+'/apps/'+sourceAppId+'/copy?appName='+NewAppName+'&targetSubscriptionLocator='+targetSubscriptionLocator, headers=Auth_Header)
    else:
        response = requests.post(api_url+'/subscriptions/0/apps/'+sourceAppId+'/copy?appName='+NewAppName, headers=Auth_Header)    
    #print (response.status_code)
    if (response.status_code == 401):
        print ("Invalid Secret access token. Please input valid Secret access token generated from https://account.cloud.tibco.com/manage/settings/oAuthTokens for TCI US region")
        exit()
    elif (response.status_code == 404 or response.status_code == 400):
        print (response.text)
        exit()

    print(response.json())
    resp_dict=json.loads(json.dumps(response.json()))
    appId=resp_dict['appId']
    print('\n***** App ID of copied app ****' , appId)
    return appId

#Get App Details
def get_app_details(appId,targetSubscriptionLocator):
    if targetSubscriptionLocator !='':
        response = requests.get(api_url+'/subscriptions/'+targetSubscriptionLocator+'/apps/'+ appId, headers=Auth_Header) 
    else:
        response = requests.get(api_url+'/subscriptions/0/apps/'+ appId, headers=Auth_Header) 

      
    print('\n**** App Details *****' , response.json())  


def start_app(targetSubscriptionLocator,app_id):
    req_url=api_url+'/subscriptions/'+targetSubscriptionLocator+'/apps/'+ app_id+'/start'
    #print ('req_url=',req_url)
    if targetSubscriptionLocator !='':
        response = requests.post(req_url, headers=Auth_Header) 
    else:
        response = requests.post(api_url+'/subscriptions/0/apps/'+ app_id+'/start', headers=Auth_Header) 
      
    print('\n**** App Started *****' , response.json())  


def test_endpoints(targetSubscriptionLocator,app_id,path,method,body):

    response = requests.get(api_url+'/subscriptions/'+targetSubscriptionLocator+'/apps/'+ app_id+'/endpoints', headers=Auth_Header) 
    resp_dict=json.loads(json.dumps(response.json()))
    req_url=resp_dict[0]['url']
    time.sleep(20)

    if method == 'get':
        print ("**** get req url", req_url+path)
        resp = requests.get(req_url+path)
        print ("*****Endpoint Response Code***",resp.status_code)
        print ("*****Endpoint Response ***",resp.json())
    elif method == 'post':
        print ("**** post req url", req_url+path+body)
        resp = requests.post(req_url+path,data=body)
        print ("*****Endpoint Response Code***",resp.status_code)
        print ("*****Endpoint Response ***",resp.json())
    elif method == 'put':
        print ("**** put req url", req_url+path+body)
        resp = requests.put(req_url+path,data=body)
        print ("*****Endpoint Response Code***",resp.status_code)
        print ("*****Endpoint Response ***",resp.json()) 
    else:
        print (" **** Invalid method ****")

def override_app_props(subscriptionLocator,app_id,variableType,override_app_prop_json):
    print ("***** Overriding App Prop******** ", override_app_prop_json)
    response = requests.put(api_url+'/subscriptions/'+subscriptionLocator+'/apps/'+ app_id+'/env/variables?variableType='+variableType, headers=Auth_Header,data=override_app_prop_json)
    print (response.status_code)
    print (response.text)

def delete_app(subscriptionLocator,app_id):
    print ("***** Deleting app with appid: ", app_id)
    response = requests.delete(api_url+'/subscriptions/'+subscriptionLocator+'/apps/'+ app_id, headers=Auth_Header)
    print (response.status_code)
    print (response.text)


def main():
    get_userInfo()
    #app_id=copy_app(sourceAppId,newAppName,subscriptionLocator,targetSubscriptionLocator)
    download_app_artifacts_from_githib(app_artifacts_github_path+'/flogo.json',app_artifacts_github_path+'/manifest.json')
    app_id=pushapp_using_app_artifacts(subscriptionLocator,newAppName,"true","1","true")
    get_app_details(app_id,subscriptionLocator)
    time.sleep(30)
    test_endpoints(subscriptionLocator,app_id,'/rest','get','')
    app_id_new=copy_app(app_id,newAppName,subscriptionLocator,targetSubscriptionLocator)
    start_app(targetSubscriptionLocator,app_id_new)
    time.sleep(30)
    test_endpoints(targetSubscriptionLocator,app_id_new,'/rest','get','')
    override_app_props(targetSubscriptionLocator,app_id_new,'app',override_app_prop_json)
    time.sleep(30)
    test_endpoints(targetSubscriptionLocator,app_id_new,'/rest','get','')
    delete_app(subscriptionLocator,app_id)
    delete_app(targetSubscriptionLocator,app_id_new)

if __name__ == "__main__":
    main()
