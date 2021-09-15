#!/usr/bin/env python
# Author : Nikhil Shah
# Date : 06/08/21
# This python script executes below workflow
""" We have 2 orgs we use for CI/CD in the Cooper Airlines org: Dev/QA, Staging & Pre-Production
1. The app on Dev/QA already exists and the purpose of the Jenkins pipeline is:
2. To copy a specific app from Dev/QA org to Staging  org
3. Deploy the new copied app in Staging org
4. Retrieve the endpoints of the deployed app in Staging org
5. Invoke the endpoint to "test" it """

# How to run this code -
# python3 flogo_rest_api.py <base_url> <access_token> <sourceAppId> <subscriptionLocator> <targetSubscriptionLocator> <newAppName>

import json
import requests
import time
import argparse
import os

subscriptionLocator=0
targetSubscriptionLocator=''
base_url=''
Auth_Header=''

parser = argparse.ArgumentParser()
parser.add_argument('base_url')
parser.add_argument('access_token')
parser.add_argument('sourceAppId')
parser.add_argument('subscriptionLocator')
parser.add_argument('targetSubscriptionLocator')
parser.add_argument('newAppName')
parser.add_argument('App_Artifacts_Github_Path')
args = parser.parse_args()

print ('base_url :',args.base_url)
print ('access_token :',args.access_token)
print ('sourceAppId :',args.sourceAppId)
print ('subscriptionLocator :',args.subscriptionLocator)
print ('targetSubscriptionLocator :',args.targetSubscriptionLocator)
print ('newAppName :',args.newAppName)
print ( 'App_Artifacts_Github_Path :',args.App_Artifacts_Github_Path)

base_url=args.base_url
access_token=args.access_token
sourceAppId=args.sourceAppId
subscriptionLocator=args.subscriptionLocator
targetSubscriptionLocator=args.targetSubscriptionLocator
newAppName=args.newAppName
App_Artifacts_Github_Path=args.App_Artifacts_Github_Path


Auth_Header={'Authorization' : 'Bearer '+access_token+'','Accept': 'application/json','User-Agent':'PostmanRuntime/7.28.3'}

#Get User Info
def get_UserInfo():
    try:
        response = requests.get(base_url+'/tci/v1/userinfo', headers=Auth_Header)
        #print('\n**** User Info*****' , response.json())  
        #print ("*******",response.status_code)
    except:
        print ("Please enter valid base url. For eg. https://api.cloud.tibco.com for TCI US region.")
        exit()

def download_app_artifacts_from_Githib(flogo_json_url,manifest_json_url):
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
    response = requests.post(base_url+'/tci/v1/subscriptions/'+subsLocator+'/apps?appName='+appName+'&forceOverwrite='+forceOverwrite+'&instanceCount='+instanceCount+'&retainAppProps='+retainAppProps+'', headers=Auth_Header,files=files)
    time.sleep(25)
    print ("*****Status Code****"+str(response.status_code))
    print(response.json())
    resp_dict=json.loads(json.dumps(response.json()))
    appId=resp_dict['appId']
    print('\n***** App ID of deployed app ****' , appId)
    return appId

#Copy App
def copy_App(sourceAppId,NewAppName,subscriptionLocator,targetSubscriptionLocator):
    print ("\n*****Copying App from Dev/QA org to Staging Org******")
    if targetSubscriptionLocator != '':
        response = requests.post(base_url+'/tci/v1/subscriptions/'+subscriptionLocator+'/apps/'+sourceAppId+'/copy?appName='+NewAppName+'&targetSubscriptionLocator='+targetSubscriptionLocator, headers=Auth_Header)
    else:
        response = requests.post(base_url+'/tci/v1/subscriptions/0/apps/'+sourceAppId+'/copy?appName='+NewAppName, headers=Auth_Header)    
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
def get_App_Details(appId,targetSubscriptionLocator):
    if targetSubscriptionLocator !='':
        response = requests.get(base_url+'/tci/v1/subscriptions/'+targetSubscriptionLocator+'/apps/'+ appId, headers=Auth_Header) 
    else:
        response = requests.get(base_url+'/tci/v1/subscriptions/0/apps/'+ appId, headers=Auth_Header) 

      
    print('\n**** App Details *****' , response.json())  


def start_App(targetSubscriptionLocator,app_id):
    req_url=base_url+'/tci/v1/subscriptions/'+targetSubscriptionLocator+'/apps/'+ app_id+'/start'
    #print ('req_url=',req_url)
    if targetSubscriptionLocator !='':
        response = requests.post(req_url, headers=Auth_Header) 
    else:
        response = requests.post(base_url+'/tci/v1/subscriptions/0/apps/'+ app_id+'/start', headers=Auth_Header) 
      
    print('\n**** App Started *****' , response.json())  


def get_Endpoints(targetSubscriptionLocator,app_id):
    if targetSubscriptionLocator !='':
        response = requests.get(base_url+'/tci/v1/subscriptions/'+targetSubscriptionLocator+'/apps/'+ app_id+'/endpoints', headers=Auth_Header) 
    else:
        response = requests.get(base_url+'/tci/v1/subscriptions/0/apps/'+ app_id+'/endpoints', headers=Auth_Header) 

    resp_dict=json.loads(json.dumps(response.json()))
    req_url=resp_dict[0]['url']
      
    print('\n**** App Endpoints *****' , req_url+'/postgresql')  
    print('\n ***** Testing the App Endpoint *******')
    time.sleep(20)
    print('\n ***Test Endpoint Response ***',requests.get(req_url+'/postgresql').json())

def main():
    get_UserInfo()
    #app_id=copy_App(sourceAppId,newAppName,subscriptionLocator,targetSubscriptionLocator)
    download_app_artifacts_from_Githib(App_Artifacts_Github_Path+'/flogo.json',App_Artifacts_Github_Path+'/manifest.json')
    app_id=pushapp_using_app_artifacts(subscriptionLocator,newAppName,"true","1","true")
    get_App_Details(app_id,subscriptionLocator)
    #start_App(subscriptionLocator,app_id)
    get_Endpoints(subscriptionLocator,app_id)

if __name__ == "__main__":
    main()
