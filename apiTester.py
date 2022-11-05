"""
API testing tool
"""

# TODO. graph around dependency and visual view what working on
# > testcase validate structure
# >> text
# >> number
# >> array
# >> list
# >> max , min, mimeType, of number
# required keys in response
# TODO: generator request from swagger json file
# TODO: Generator config file
# > Update/show structure view

# TODO: Bulk config file loader => implement via jenkins
# TODO: Retest loading auth params via console param stringify

# TODO: run test with unique build number and add to the documantaion the build number
#  TODO: implement jenkins job to run the test and generate the report and send it to the email

try:
    import requests
    import argparse
    import time
    import os
    import json
    from sys import exit
    from datetime import timedelta
    from datetime import datetime
    from tolls.validator import Validator
    from tolls.operations import Operations
except ImportError:
    raise Exception('Module install via: pip install requests')

try:
    from junit_xml import TestSuite, TestCase
except ImportError:
    raise Exception('Module install via: pip install junit-xml')


## base entry method to API testing
def ApiTester(endPoint, methodType, jsonReqParams, responseNumber, timeoutForAction, responseValidations,
              apiNameTestSuite="", headers="", cookies=None, skip=None,buildNumber=0):
    responseData = ""

    # skip internal validation serve the content in return
    if 'SkipValidationReturnData' in responseValidations:
        return responseData
    elif skip is not None:
        Validator(
            response="DISABLED: "+skip,
            responseValidationRules="SkipRun~GenReport",
            testSuiteName=apiNameTestSuite,
            testCaseName=apiNameTestSuite
        )
    else:
        startTime = time.time()
        responseData = Operations.Request(
            urlApi=endPoint,
            jsonReq=jsonReqParams,
            responseNumber=responseNumber,
            timeoutForAction=timeoutForAction,
            methodType=methodType,
            headers=headers,
            cookies=cookies
        )
        runtime = time.time() - startTime
        Validator(
            response=responseData,
            responseValidationRules=responseValidations,
            duration=runtime,
            testSuiteName=apiNameTestSuite,
            testCaseName=apiNameTestSuite,
            buildNumber=buildNumber
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--ConfFile', required=True, help="This file contains all previous parameters for test",
                        type=str)
    parser.add_argument('--AuthParams', required=False, help="This params contains stringify auth params",
                        type=str)
    parser.add_argument('--BuildNumber', required=False, help="This number is unique build number for each run",
                        type=str)

    args = parser.parse_args()
    ## Load data from config file
    loadedData = Operations.LoadTestData(args)
    authValidToken = ""
    cookies = None
    returnToken = ""
    if 'authentications' in loadedData:
        for auth in loadedData['authentications']:
            requestDataParams = None
            if 'returnToken' in auth['response']:
                returnToken = auth['response']['returnToken']
            if 'requestDataParams' in auth['request']:
                if 'authParams' in loadedData:
                    requestDataParams = loadedData['authParams']
                else:
                    requestDataParams = auth['request']['requestDataParams']
            if 'authUrl' in loadedData:
                endPointUrl = loadedData['authUrl']
            else:
                endPointUrl = loadedData['url']
            authValidToken = ApiTester(
                endPoint=endPointUrl + auth['request']['endPoint'],
                methodType=auth['request']['method'],
                jsonReqParams=requestDataParams,
                responseNumber=auth['response']['responseStatus'],
                timeoutForAction=auth['response']['timeoutForActionSec'],
                responseValidations=auth['response']['validationRules'] + "~SkipValidationReturnData",
                apiNameTestSuite=auth['response']['nameTestSuite'],
                headers=Operations.HeadersLoader(
                    header=auth['request'],
                    findString=returnToken,
                    replaceData=authValidToken
                )
                # cookies=authValidToken['cookies']
            )
    if 'cookies' in authValidToken:
        cookies = authValidToken['cookies']
    for config in loadedData['config']['endPoints']:
        skipDescription = None
        if 'skipped' in config:
            skipDescription = config['skipped']
        returnData = ApiTester(
            endPoint=loadedData['config']['url'] + config['request']['endPoint'],
            methodType=config['request']['method'],
            jsonReqParams=config['request']['requestDataParams'],
            responseNumber=config['response']['responseStatus'],
            timeoutForAction=config['response']['timeoutForActionSec'],
            responseValidations=config['response']['validationRules'],
            apiNameTestSuite=config['response']['nameTestSuite'],
            headers=Operations.HeadersLoader(
                header=config['request']['headers'],
                findString=returnToken,
                replaceData=authValidToken
            ),
            cookies=cookies,
            skip=skipDescription
        )
        if 'SkipValidationReturnData' in config['response']['validationRules']:
            print(returnData)
        time.sleep(1)
