# CI/CD workflow for deploying/copying/testing applications to TIBCO Cloud Integration using python script hosted on github..


## Description

This sample demonstrates a simple worflow about how to deploy applications to TCI, copy them from one org to another, run the app, and test the endpoints.

""" We have 2 orgs we use for CI/CD in the Cooper Airlines org: Dev/QA, Staging & Pre-Production
1. The app on Dev/QA already exists and the purpose of the Jenkins pipeline is:
2. To copy a specific app from Dev/QA org to Staging  org
3. Deploy the new copied app in Staging org
4. Retrieve the endpoints of the deployed app in Staging org
5. Invoke the endpoint to "test" it """

## Prerequisites

* Generate OAuth2 access token for Integration Domain from TIBCO Cloud Settings page - https://account.cloud.tibco.com/manage/settings/oAuthTokens
* Install jenkins - https://www.jenkins.io/doc/book/installing/


## Run the CI/CD pipeline

1. Get the sourceAppId of the app that you would like to copy from the TCI web ui

2. Get the subscriptionLocator of the source org and target org from the userinfo platform API as shown below -
![Select import](import-screenshots/7.APICalls.png)


3. Start the jenkins and login to jenkins url - http://localhost:8080/

4. Create a freestyle project

5. Select the project and click on Configure. Check This project is parameterized
Add the params as base_url, access_token, sourceAppId, subscriptionLocator, targetSubscriptionLocator, newAppName and their default values
![Select import](import-screenshots/1.Build_params.png)

6. Select SCM as git and configure using the repo url as shown below -
![Select import](import-screenshots/2.SCM.png)

7. Add build step as shown below -
![Select import](import-screenshots/3.Build.png)

8. Click on Save and click on Build with Parameters as below -
![Select import](import-screenshots/4.Build_with_params.png)

9. Check the console output as below and see that the app is copied from Dev/QA org to Staging Org and also the app is running and the endpoints are being tested.
![Select import](import-screenshots/5.Console_output.png)

10. Check the app is copied to and running in TCI in Pre-Production/Staging Org -
![Select import](import-screenshots/6.CopiedApp.png)


