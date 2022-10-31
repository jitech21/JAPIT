import json
import os
import requests

class Operations:
    ## Load Json config file content
    def LoadTestData(args):
        if args.ConfFile is not None:
            loadData = Operations.LoadContent(nameReportFolder="", file=args.ConfFile)
            ConfigFile = json.load(loadData)
            return ConfigFile

    ## Create folder if not exist
    def GenFolder(nameReportFolder):
        if not os.path.exists(nameReportFolder):
            os.mkdir(nameReportFolder)
            print("Directory ", nameReportFolder, " Created ")
        return nameReportFolder

    def HeadersLoader(header, findString, replaceData):
        returnHeader = {}
        if 'cookies' in header:
            headerData = header['cookies']
        elif 'headers' in header:
            headerData = header['headers']
        else:
            return
        if replaceData != '':
            replaceData = replaceData['text']
            if 'access_token' in replaceData:
                replaceData = json.loads(replaceData)['access_token']

        for key, val in headerData.items():
            findIn = ''
            if 'Authorization' in key:
                findIn = val
            elif 'Cookie' in key:
                findIn = val

            if findString in findIn:
                findIn = findIn.replace(findString, replaceData)
                returnHeader[key] = findIn
            else:
                returnHeader[key] = val
        return returnHeader

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
            response = requests.request(
                method=methodType,
                url=urlApi,
                cookies=cookies,
                params=params,
                data=jsonReq,
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
                    "json": response.json(),
                    "status_code": response.status_code,
                    "cookies": response.cookies
                }
            else:
                return {
                    "text": "FAILURE: API endpoint: " + str(urlApi) + " returned this response status_code: " + str(
                        response.status_code),
                    "status_code": response.status_code
                }