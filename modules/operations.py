import json
import os
import requests

class Operations:
    ## Load Json config file content
    def LoadTestData(args):
        authParams = {}
        buildNumber = 0
        if args.ConfFile is not None:
            loadData = Operations.LoadContent(nameReportFolder="", file=args.ConfFile)
            configFile = json.load(loadData)
        if args.AuthParams is not None:
            authParams = json.loads(args.AuthParams)
        if args.BuildNumber is not None:
            buildNumber = args.BuildNumber
        return {"config": configFile, "authParams": authParams, "buildNumber": buildNumber}

    ## Create folder if not exist
    def GenFolder(nameReportFolder):
        if not os.path.exists(nameReportFolder):
            os.mkdir(nameReportFolder)
            print("Directory ", nameReportFolder, " Created ")
        return nameReportFolder

    def HeadersLoader(header, findString, replaceData):
        if 'cookies' in header:
            headerData = header['cookies']
        elif 'headers' in header:
            headerData = header['headers']
        else:
            return
        return Operations.MatchValue(replaceData,headerData,findString)

    ## Write tmp log data file
    def WriteOpenData(fileName, folderName, writeData, openType="w"):
        # TODO implement open as function not create response data if exist
        file = open(
            folderName + "/" + fileName,
            openType
        )
        if (openType == 'w') | (openType == 'a'):
            file.write(
                writeData
            )
        file.close()
        return file

    ## Loading content from the file
    def LoadContent(nameReportFolder, file):
        return open(nameReportFolder + file, 'r')

    ## This action perform communication via requests
    def Request(urlApi, responseNumber, timeoutForAction, methodType, headers, jsonReq=None, cookies=None):
        try:
            params = jsonReq

            if methodType == "POST":
                params = None
                jsongraphQL = jsonReq
            elif methodType == "GET":
                params = jsonReq
                jsongraphQL = None
            if "query" in jsonReq:
                jsongraphQL = jsonReq
                params = None
            response = requests.request(
                method=methodType,
                url=urlApi,
                cookies=cookies,
                params=params,
                json=jsongraphQL,
                headers=headers,
                timeout=timeoutForAction
            )

        except Exception as e:
            return {
                "text": "ERROR: " + str(e),
                "status_code": ''
            }
        else:
            if int(responseNumber) == response.status_code:
                return {
                    "text": response.text,
                    "status_code": response.status_code,
                    "cookies": response.cookies
                }
            else:
                return {
                    "text": "FAILURE: API endpoint: " + str(urlApi) + " returned this response status_code: " + str(
                        response.status_code),
                    "status_code": responseNumber
                }

    def MatchValue(loadData,replaceData,findString):
        returnHeader = {}
        if loadData != '':
            loadData = json.loads(loadData['text'])
            if 'access_token' in loadData:
                loadData = loadData['access_token']
            elif 'data' in loadData:
                loadData = loadData['data']

        for key, val in loadData.items():
            findIn = ''
            if 'Authorization' in key:
                findIn = val
            elif 'Cookie' in key:
                findIn = val
            elif findString.replace('$', '') in key:
                loadData = str(loadData[findString.replace('$', '')])
                findIn = replaceData

            if findString in findIn:
                findIn = findIn.replace(findString, loadData)
                returnHeader[key] = findIn
            else:
                returnHeader[key] = val
        return returnHeader