#!/usr/bin/env python
# Author : Nikhil Shah
# Date : 06/08/21
# Workflow 
""" We have 3 orgs we use for CI/CD in the Cooper Airlines org: Dev/QA, Staging, Production
1. The app on Dev/QA already exists and the purpose of the Jenkins pipeline is:
2. To copy a specific app from Dev/QA org to Staging  org
3. Deploy the new copied app in Staging org
4. Retrieve the endpoints of the deployed app in Staging org
5. Invoke the endpoint to "test" it
6. Copy the app in Staging org to Production org
7. Deploy it
8. Retrieve the endpoints again
9. Test the endpoint """

# How to run this code -
# python3 flogo_rest_api.py <base_url> <access_token> <sourceAppId> <subscriptionLocator> <targetSubscriptionLocator> <newAppName>
# python3 flogo_rest_api.py https://api.cloud.tibco.com CIC~1jMeVjaKXXyiYyMA3BN2US7i 4zq3ltkemzksoyir7h6z25hbe55yf5he ng5qdjk68q6_3w50jbauc3_mjs48zv uyyi2a-fw8fouaskjkqiojhimxmaf8 FlogoDemoApp

import json
import requests
import time
import argparse

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
args = parser.parse_args()

print ('base_url :',args.base_url)
print ('access_token :',args.access_token)
print ('sourceAppId :',args.sourceAppId)
print ('subscriptionLocator :',args.subscriptionLocator)
print ('targetSubscriptionLocator :',args.targetSubscriptionLocator)
print ('newAppName :',args.newAppName)

base_url=args.base_url
access_token=args.access_token
sourceAppId=args.sourceAppId
subscriptionLocator=args.subscriptionLocator
targetSubscriptionLocator=args.targetSubscriptionLocator
newAppName=args.newAppName


Auth_Header={'Authorization' : 'Bearer '+access_token+'','Accept': 'application/json','User-Agent':'PostmanRuntime/7.28.3'}

#Get User Info
def get_UserInfo():
    response = requests.get(base_url+'/tci/v1/userinfo', headers=Auth_Header)
    #print('\n**** User Info*****' , response.json())  


#Copy App
def copy_App(sourceAppId,NewAppName,subscriptionLocator,targetSubscriptionLocator):
    if targetSubscriptionLocator != '':
        response = requests.post(base_url+'/tci/v1/subscriptions/'+subscriptionLocator+'/apps/'+sourceAppId+'/copy?appName='+NewAppName+'&targetSubscriptionLocator='+targetSubscriptionLocator, headers=Auth_Header)
    else:
        response = requests.post(base_url+'/tci/v1/subscriptions/0/apps/'+sourceAppId+'/copy?appName='+NewAppName, headers=Auth_Header)    
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

#https://api.cloud.tibco.com/tci/v1/subscriptions/uyyi2a-fw8fouaskjkqiojhimxmaf8/apps/e4sfelr3cuybr2gqls67w4gym7h3pqlz/start
def start_App(targetSubscriptionLocator,app_id):
    req_url=base_url+'/tci/v1/subscriptions/'+targetSubscriptionLocator+'/apps/'+ app_id+'/start'
    #print ('req_url=',req_url)
    if targetSubscriptionLocator !='':
        response = requests.post(req_url, headers=Auth_Header) 
    else:
        response = requests.post(base_url+'/tci/v1/subscriptions/0/apps/'+ app_id+'/start', headers=Auth_Header) 
      
    print('\n**** App Started *****' , response.json())  

#https://api.cloud.tibco.com/tci/v1/subscriptions/uyyi2a-fw8fouaskjkqiojhimxmaf8/apps/e4sfelr3cuybr2gqls67w4gym7h3pqlz/endpoints
def get_Endpoints(targetSubscriptionLocator,app_id):
    if targetSubscriptionLocator !='':
        response = requests.get(base_url+'/tci/v1/subscriptions/'+targetSubscriptionLocator+'/apps/'+ app_id+'/endpoints', headers=Auth_Header) 
    else:
        response = requests.get(base_url+'/tci/v1/subscriptions/0/apps/'+ app_id+'/endpoints', headers=Auth_Header) 

    resp_dict=json.loads(json.dumps(response.json()))
    req_url=resp_dict[0]['url']
      
    print('\n**** App Endpoints *****' , req_url+'/rest')  
    time.sleep(15)
    print('\n ***Test Endpoint Response ***',requests.get(req_url+'/rest').json())

def main():
    

    
    #base_url='https://api.cloud.tibco.com'
    #access_token= 'CIC~1jMeVjaKXXyiYyMA3BN2US7i'
    #sourceAppId='4zq3ltkemzksoyir7h6z25hbe55yf5he' #FlogoDemoApp
    #newAppName='FlogoDemoApp'
    #subscriptionLocator='ng5qdjk68q6_3w50jbauc3_mjs48zv' #Akron - Dev/QA Org
    #targetSubscriptionLocator='uyyi2a-fw8fouaskjkqiojhimxmaf8' #Pre-Production / Staging Org
    get_UserInfo()
    app_id=copy_App(sourceAppId,newAppName,subscriptionLocator,targetSubscriptionLocator)
    #app_id='m6ykfelr46j6mumauyzbducstfhr5tt3'
    get_App_Details(app_id,targetSubscriptionLocator)
    start_App(targetSubscriptionLocator,app_id)
    get_Endpoints(targetSubscriptionLocator,app_id)

if __name__ == "__main__":
    main()
