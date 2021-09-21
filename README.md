# CI/CD workflow for deploying/copying/testing FLOGO applications in TIBCO Cloud Integration using python script hosted on github.


## Description

This sample demonstrates a simple workflow mentioned below about how to deploy FLOGO apps to TCI, copy them from one org to another, run the app, and test the endpoints.

1. Checkout Flogo app json (with Connection) and manifest json from GitHub
2. Deploy the app to Dev/QA Org using TCI Platform API
3. Test the app endpoint
4. Copy the app to Staging Org
5. Override the App Prop in Staging Org
6. Test the Endpoint
7. Delete the app from Dev/QA Org

## Prerequisites

* Generate OAuth2 access token for Integration Domain from TIBCO Cloud Settings page - https://account.cloud.tibco.com/manage/settings/oAuthTokens
* Install jenkins - https://www.jenkins.io/doc/book/installing/
* Install python3 on the host system where jenkins is running
* Install python requests module using - ```pip install requests```

## Running the python script stand-alone

In order to do unit testing before creating the CI/CD pipeline, it is recommended to run the python script stand alone to make sure, it is working as per the workflow.

```
python3 flogo_rest_api.py <base_url> <access_token> <sourceAppId> <subscriptionLocator> <targetSubscriptionLocator> <newAppName> <App_Artifacts_Github_Path> <Override_App_Prop_Json>
```

where 
* **base_url** is the url of API as per region of your TIBCO Cloud™ Account subscription. For eg, for US region, it is ```https://api.cloud.tibco.com/tci/v1``` . Refer [this](https://integration.cloud.tibco.com/docs/#Subsystems/tci-api/home.html?TocPath=TIBCO%2520Cloud%25E2%2584%25A2%2520Integration%2520API%257C_____0) doc for more info.
* **access_token** is the OAuth2 Bearer access token ot be generated as mentioned in Prerequisites section
* **sourceAppId** (Optional) Only required if you already have an app in the org and need to copy it to another org. You can pass 0 as value
* **subscriptionLocator** Locator of the subscription. Enter 0 for the subscription associated with your OAuth token. You can get the subscriptionLocator for your Org using this API ```https://api.cloud.tibco.com/tci/v1/userinfo```
* **targetSubscriptionLocator** Subscription locator of the target organization. Enter 0 for the subscription associated with your OAuth token. You can get the subscriptionLocator for your target Org using this API ```https://api.cloud.tibco.com/tci/v1/userinfo```
* **newAppName** New app name. Name must be unique in the target organization.
* **App_Artifacts_Github_Path**  Raw file path on github where your manifest.json and flogo.json are located. For eg ```https://raw.githubusercontent.com/nikhilshah26/TCI-FLOGO-CICD/main/Flogo_App```
* **Override_App_Prop_Json** JSON for Application Properties/Variables, Engine Variables to be updated. Description and data type are ignored for engine and app variables.
For eg: ```[{"description":"string","name":"PostgreSQL.PostgreSQLConn.Host","type":"string","value":"10.20.30.40"}]```


## Running as CI/CD pipeline using jenkins

1. Get the subscriptionLocator of the source org and target org from the userinfo platform API as shown below -
![Select import](import-screenshots/7.APICalls.png)

2. Start the jenkins and login to jenkins url - http://localhost:8080/

3. Create a freestyle project

4. Select the project and click on Configure. Check This project is parameterized
Add the params as base_url, access_token, sourceAppId, subscriptionLocator, targetSubscriptionLocator, newAppName and their default values
![Select import](import-screenshots/1.General.png)
![Select import](import-screenshots/2.Build_params.png)

5. Select SCM as git and configure using the repo url as shown below -
![Select import](import-screenshots/3.SCM.png)

6. Add build step as shown below -
![Select import](import-screenshots/4.BuildTrigger_and_BuildStep.png)

7. Click on Save and click on Build with Parameters as below -
![Select import](import-screenshots/5.Build_with_params.png)

8. Check the console output as below and see that the app is copied from Dev/QA org to Staging Org and also the app is running and the endpoints are being tested.
![Select import](import-screenshots/5.Console_output.png)

9. Check the app is copied to and running in TCI in Pre-Production/Staging Org -
![Select import](import-screenshots/6.CopiedApp.png)

10. You can also configure GitHub Webhooks Trigger, to trigger your jenkins job. Please see screenshot below on how to configure webhooks on Github -
![Select import](import-screenshots/6.Webhooks.png)

## Help

Please refer [TIBCO Cloud<sup>&trade;</sup> Integration API documentation](https://integration.cloud.tibco.com/docs/#Subsystems/tci-api/home.html?TocPath=TIBCO%2520Cloud%25E2%2584%25A2%2520Integration%2520API%257C_____0) and Swagger Page URL [docs.tibco.com](https://api.cloud.tibco.com/tci/docs/) for additional information.

## Feedback
If you have feedback, don't hesitate to talk to us!

* Submit feature requests on our [TCI Ideas](https://ideas.tibco.com/?project=TCI) or [FE Ideas](https://ideas.tibco.com/?project=FE) portal
* Ask questions on the [TIBCO Community](https://community.tibco.com/answers/product/344006)
* Send us a note at `tci@tibco.com`


