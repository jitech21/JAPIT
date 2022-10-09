'''
API testing tool
'''

# TODO: retest all type of requests
# TODO: validation of reponse
## TODO: validate keys
## TODO: validate type of value in define keys
# TODO: authentication via OATH2.0 integration with
# TODO: keycloack one url and another url and then session number
# TODO: ADD commant
# TODO: Create documantion on my own Web site
# TODO. graph around dependency and visual view what working on

try:
    import requests
    import argparse
    import time
    import os
    import json
    from sys import exit
    from datetime import datetime
except ImportError:
    raise Exception('Module install via: pip install requests')

try:
    from junit_xml import TestSuite, TestCase
except ImportError:
    raise Exception('Module install via: pip install junit-xml')

try:
    from junitparser import JUnitXml
except ImportError:
    raise Exception('Module install via: pip install junitparser')


def GenFolder(nameReportFolder):
    if not os.path.exists(nameReportFolder):
        os.mkdir(nameReportFolder)
        print("Directory ", nameReportFolder, " Created ")
    return nameReportFolder


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


def loadContent(nameReportFolder, file):
    return open(nameReportFolder + file, 'r')


def Request(urlApi, jsonReq, responseNumber, timeoutForAction, methodType):
    try:
        if methodType == "POST":
            response = requests.post(urlApi, json=jsonReq, timeout=timeoutForAction)
        else:
            response = requests.get(urlApi, timeout=timeoutForAction)
    except Exception as e:
        return f"ERROR: NOT OK: {str(e)}"
    else:
        if int(responseNumber) == response.status_code:
            return response.text
        else:
            return f"ERROR: API address: {str(urlApi)} returned this response status_code: {str(response.status_code)}"


def ApiTester(urlApi, methodType, jsonReq, responseNumber, timeoutForAction, responseFormat, expectedValues,
              apiNameTestCase="", apiNameTestSuite=""):
    responseData = ""
    startTime = time.time()
    responseData = Request(
        urlApi=urlApi,
        jsonReq=jsonReq,
        responseNumber=responseNumber,
        timeoutForAction=timeoutForAction,
        methodType=methodType
    )

    runtime = time.time() - startTime
    Validator(
        response=responseData,
        responseFormat=responseFormat,
        expectedValues=expectedValues,
        duration=runtime,
        testSuiteName=apiNameTestSuite,
        testCaseName=apiNameTestCase
    )


class Validator:
    def __init__(self, response, responseFormat="", expectedValues="", duration=0.0, testSuiteName="", testCaseName=""):
        self.response = response
        self.expectedValues = expectedValues
        self.duration = duration
        self.testCaseName = testCaseName
        self.testSuiteName = testSuiteName
        responseValidationRules = responseFormat.split('~')
        if len(responseValidationRules) == 1:
            getattr(self, 'Case' + responseValidationRules[0])()
        else:
            getattr(self, 'CaseResponse')()
            getattr(self, 'CasePrevoiusDataValidation')()
            for validationRules in responseValidationRules:
                getattr(self, 'Case' + validationRules)()

        # TODO: implement config file in apis
        # TODO: many validation rules
        # TODO: test result: test suite
        # > testcase data come
        # > testcase validate structure
        # >> text
        # >> number
        # >> array
        # >> list

    def CaseResponse(self):
        ResultGenerator(
            nameReportFolder="reports/",
            nameReportFile=self.testCaseName,
            testSuiteName=self.testSuiteName,
            testCaseName=self.testCaseName + " - Response come",
            duration=self.duration,
            testResult=""
        )

    def CaseCreateResponseFileOutput(self):
        createNewFile = self.testSuiteName.replace("/", "%")
        folderName = "apis/" + createNewFile + "/response"
        WriteOpenData(fileName=createNewFile + '.json', folderName=folderName, writeData=self.response, openType="w")

    def CasePrevoiusDataValidation(self):
        createNewFile = self.testSuiteName.replace("/", "%")
        folderName = "apis/" + createNewFile + "/response/"
        if os.path.exists(folderName + createNewFile + ".json"):
            fileLoad = loadContent(nameReportFolder=folderName, file=createNewFile + ".json")
            expectedData = fileLoad.read()
            if self.response == expectedData:
                errorMessage = ''
            else:
                errorMessage = "FAILURE: The response is not same as expected:", self.response
            ResultGenerator(
                nameReportFolder="reports/",
                nameReportFile=self.testCaseName,
                testSuiteName=self.testSuiteName,
                testCaseName=self.testCaseName + " - validateExpectedData",
                duration=0.0,
                testResult=errorMessage
            )
            print(8)
        else:
            self.CaseCreateResponseFileOutput()

    def CaseText(self):
        # TODO: TBD
        print("2")

    def CaseNumber(self):
        # TODO: TBD
        print("3")

    def CaseArray(self):
        # TODO: TBD
        print("4")

    def CaseList(self):
        # TODO: TBD
        print("5")

    def CaseCheckValueInstructure(self):
        # TODO: TBD
        print("10")

    def CaseJson(self):
        errorMessage = ""
        validator = Validator(response=self.response, responseFormat="IsJSON")
        isValidStructure = True
        if self.response.startswith("ERROR:"):
            errorMessage = self.response
        elif not validator.CaseIsJSON():
            errorMessage = "FAILURE: The response is not in json format:", self.response
            isValidStructure = False

        ResultGenerator(
            nameReportFolder="reports/",
            nameReportFile=self.testCaseName,
            testSuiteName=self.testSuiteName,
            testCaseName=self.testCaseName + " - validateJsonStructure",
            duration=0.0,
            testResult=errorMessage
        )
        return isValidStructure

    def CaseIsJSON(self):
        try:
            json.loads(self.response)
        except ValueError as e:
            print('invalid json: %s' % e)
            return None
        return True

    def CaseGenReport(self):
        # GEN. XML TEST report
        ResultGenerator(
            nameReportFolder="reports/",
            nameReportFile=self.testCaseName,
            testSuiteName=self.testSuiteName,
            testCaseName=self.testCaseName,
            duration="",
            testResult="",
            genXMLReport=True
        )


class ResultGenerator:

    def __init__(self, nameReportFolder, nameReportFile, testSuiteName, testCaseName, duration, testResult,
                 genXMLReport=False):
        self.parsedResult = None
        self.testSuiteName = testSuiteName
        self.testCaseName = testCaseName
        self.duration = duration
        self.testResult = testResult
        self.nameReportFolder = nameReportFolder
        self.nameReportFile = nameReportFile
        if genXMLReport:
            self.genXmlReport(self.genReportFromFolder())
        else:
            self.genTmpRepostFile()

    def removeLogFileThen(self, nameOfFile):
        now = datetime.now()
        parsedDateName = nameOfFile.replace('~' + self.nameReportFile.replace("/", "%") + '.log', '')
        parsedDateName = parsedDateName.replace('reports/', '')
        if parsedDateName < now.strftime("%Y-%m-%d"):
            print('Remove file: ', nameOfFile)
            os.remove(nameOfFile)

    def genTmpRepostFile(self):
        GenFolder(self.nameReportFolder)
        fileName = str(datetime.now().strftime("%Y-%m-%d")) + '~' + self.nameReportFile.replace("/", "%") + '.log'
        data = str(datetime.now().strftime("%Y-%m-%d_%H:%M:%S")) + '~' + str(self.testSuiteName) + '~' + str(
            self.testCaseName) + '~' + str(self.duration) + '~' + str(self.testResult) + '\n'
        WriteOpenData(fileName=fileName, folderName=self.nameReportFolder, writeData=data, openType='a')

    def genReportFromFolder(self):
        for file in os.listdir(self.nameReportFolder):
            if file.endswith(".log"):
                self.removeLogFileThen(self.nameReportFolder + file)
                testSuite = self.CreateTestSuite(file=file)
        return testSuite

    def genXmlReport(self, TestSuiteData):
        with open(
                self.nameReportFolder + self.nameReportFile + "-" + str(datetime.now().strftime("%Y-%m-%d")) + ".xml",
                'w') as file:
            TestSuite.to_file(file_descriptor=file, test_suites=TestSuiteData, prettyprint=True)

    def CreateTestSuite(self, file):
        testSuites = []
        testCases = []
        with loadContent(self.nameReportFolder.replace("/", "") + '/', file) as f:
            dataFileContent = f.read()
            linesFileContent = dataFileContent.splitlines()
            previousValueTime = ""
            for index, lineFileContent in enumerate(linesFileContent, start=0):
                splitLine = lineFileContent.split('~')
                if (len(testSuites) == 0) & (len(testCases) > 0):
                    testSuites.append(
                        TestSuite(name=self.testSuiteName,
                                  test_cases=testCases,
                                  timestamp=str(splitLine[0])
                                  )
                    )
                elif (index > 0) & (previousValueTime != str(splitLine[0])) :
                    testSuites.append(
                        TestSuite(name=self.testSuiteName,
                                  test_cases=testCases,
                                  timestamp=str(splitLine[0])
                                  )
                    )
                    testCases = []
                testCase = self.CreateTestCase(splitLine)
                testCases.append(testCase)

                previousValueTime = splitLine[0]
        return testSuites

    def CreateTestCase(self, parsedResult):
        testCase = TestCase(
            name=parsedResult[2],
            elapsed_sec=float(parsedResult[3])
        )
        result = parsedResult[4]
        if 'ERROR:' in result:
            testCase.add_error_info(message=result, output=result)
        elif 'DISABLED:' in result:
            testCase.add_skipped_info(message=result, output=result)
        elif 'FAILURE:' in result:
            # TODO: confirm change status in test case fail -> pass, pass-> fail
            testCase.add_failure_info(message=result, output=result)
        return testCase


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--UrlApi", required=True, help="WebSite specify which web site tested.",
                        type=str
                        )
    parser.add_argument("--MethodType", required=False, help="Select with method should used (POST,GET)",
                        type=str
                        )
    parser.add_argument('--RequestData', required=False,
                        help="RequestedData for POST action.",
                        type=str
                        )
    parser.add_argument('--ResponseNumber', required=True,
                        help="ResponseNumber which number shlould expect for passing test (for ex. 200).",
                        type=int
                        )
    parser.add_argument('--TimeoutForAction', required=True,
                        help="TimeoutForAction delay for provide data for text detection on web site.",
                        type=int
                        )
    parser.add_argument('--ExpectedValues', required=True,
                        help="ResponseValidator expected response.",
                        type=str
                        )
    parser.add_argument('--ResponseFormat', required=True,
                        help="ResponseFormat which type of response should be expected. types: (Text, Number, Json, Array, JsonStructure, CheckValueInstructure)",
                        type=str
                        )
    parser.add_argument('--ApiNameTestSuite', required=True,
                        help="ApiNameTestSuite name of test case",
                        type=str
                        )
    parser.add_argument('--ApiNameTestCase', required=True,
                        help="ApiNameTestCase name of test case",
                        type=str
                        )

    args = parser.parse_args()
    if args.MethodType == 'POST' and Validator(response=args.RequestData).CaseIsJSON() is False:
        print(args)
        print("It is necessary set the parameter 'RequestData' for POST method on valid escape json: \n",
              args.RequestData
              )
        exit(1)

    ApiTester(
        urlApi=args.UrlApi,
        methodType=args.MethodType,
        jsonReq=args.RequestData,
        responseNumber=args.ResponseNumber,
        timeoutForAction=args.TimeoutForAction,
        responseFormat=args.ResponseFormat,
        expectedValues=args.ExpectedValues,
        apiNameTestCase=str(args.ApiNameTestCase) if args.ApiNameTestCase != "" else args.UrlApi,
        apiNameTestSuite=str(args.ApiNameTestSuite) if args.ApiNameTestSuite != "" else args.UrlApi
    )
