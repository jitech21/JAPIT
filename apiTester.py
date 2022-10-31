'''
API testing tool
'''

# TODO: Create documentation on my own Web site
# TODO. graph around dependency and visual view what working on
# > testcase data come
# > testcase validate structure
# >> text
# >> number
# >> array
# >> list
# >> max , min, mimeType, of number
# required keys in response
# TODO: generator request from swagger json file
#TODO: GraphQL implementaion
# -> https://www.geeksforgeeks.org/get-and-post-requests-in-graphql-api-using-python-requests/
# -> https://lucasconstantino.github.io/graphiql-online/

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
              apiNameTestSuite="",  headers="", cookies=None):
    responseData = ""
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

    # skip internal validation serve the content in return
    if 'SkipValidationReturnData' in responseValidations:
        return responseData
    Validator(
        response=responseData,
        responseValidationRules=responseValidations,
        duration=runtime,
        testSuiteName=apiNameTestSuite,
        testCaseName=apiNameTestSuite
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--ConfFile', required=True, help="This file contains all previous parameters for test",
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
                responseValidations=auth['response']['validationRules']+"~SkipValidationReturnData",
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
    for config in loadedData['endPoints']:
        returnData = ApiTester(
            endPoint=loadedData['url'] + config['request']['endPoint'],
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
            cookies=cookies
        )
        if 'SkipValidationReturnData' in config['response']['validationRules']:
            print(returnData)
        time.sleep(1)