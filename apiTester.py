'''
API testing tool
'''

# TODO: retest all type of requests
# TODO: keycloack one url and another url and then session number
# TODO: Create documentation on my own Web site
# TODO. graph around dependency and visual view what working on
# TODO: test result: test suite
# > testcase data come
# > testcase validate structure
# >> text
# >> number
# >> array
# >> list
# >> max , min, mimeType, of number
# required keys in response
# TODO: generator request from swagger json file

try:
    import requests
    import argparse
    import time
    import os
    import json
    from sys import exit
    from datetime import timedelta
    from datetime import datetime

except ImportError:
    raise Exception('Module install via: pip install requests')

try:
    from junit_xml import TestSuite, TestCase
except ImportError:
    raise Exception('Module install via: pip install junit-xml')


## Load Json config file content
def LoadTestData(args):
    if args.ConfFile is not None:
        loadData = LoadContent(nameReportFolder="", file=args.ConfFile)
        ConfigFile = json.load(loadData)
        return ConfigFile


## Create folder if not exist
def GenFolder(nameReportFolder):
    if not os.path.exists(nameReportFolder):
        os.mkdir(nameReportFolder)
        print("Directory ", nameReportFolder, " Created ")
    return nameReportFolder


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


## base entry method to API testing
def ApiTester(endPoint, methodType, jsonReq, responseNumber, timeoutForAction, responseValidations,
              apiNameTestCase="", apiNameTestSuite=""):
    responseData = ""
    startTime = time.time()
    responseData = Request(
        urlApi=endPoint,
        jsonReq=jsonReq,
        responseNumber=responseNumber,
        timeoutForAction=timeoutForAction,
        methodType=methodType
    )

    runtime = time.time() - startTime
    Validator(
        response=responseData,
        responseFormat=responseValidations,
        duration=runtime,
        testSuiteName=apiNameTestSuite,
        testCaseName=apiNameTestCase
    )


### Class validate response
class Validator:
    def __init__(self, response, responseFormat="", duration=0.0, testSuiteName="", testCaseName=""):
        self.response = response
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

    ## Validator if response come
    def CaseResponse(self):
        ResultGenerator(
            nameReportFolder="reports/",
            nameReportFile=self.testCaseName,
            testSuiteName=self.testSuiteName,
            testCaseName=self.testCaseName + " - Response come",
            duration=self.duration,
            testResult=""
        )

    ## Create expected data validation file if not exist
    def CaseCreateResponseFileOutput(self):
        createNewFile = self.testSuiteName.replace("/", "%")
        folderName = "apis/" + createNewFile + "/response"
        WriteOpenData(fileName=createNewFile + '.json', folderName=folderName, writeData=self.response, openType="w")

    ## Validator if data should be same
    def CasePrevoiusDataValidation(self):
        createNewFile = self.testSuiteName.replace("/", "%")
        folderName = "apis/" + createNewFile + "/response/"
        if os.path.exists(folderName + createNewFile + ".json"):
            fileLoad = LoadContent(nameReportFolder=folderName, file=createNewFile + ".json")
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
        else:
            self.CaseCreateResponseFileOutput()

    ## validate text
    def CaseText(self):
        # TODO: TBD
        print("2")

    ## validate number
    def CaseNumber(self):
        # TODO: TBD
        print("3")

    ##  validate array
    def CaseArray(self):
        # TODO: TBD
        print("4")

    ## validate data in structure
    def CaseCheckValueInStructure(self):
        # TODO: TBD
        print("10")

    ## validate json response
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

    ## validate parsable JSON
    def CaseIsJSON(self):
        try:
            json.loads(self.response)
        except ValueError as e:
            print('invalid json: %s' % e)
            return None
        return True

    ## createReport
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


## junit XML report
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

    ## Remove unused file
    def removeLogFileThen(self, nameOfFile):
        now = datetime.now()
        parsedDateName = nameOfFile.replace('~' + self.nameReportFile.replace("/", "%") + '.log', '')
        parsedDateName = parsedDateName.replace('reports/', '')
        if parsedDateName < now.strftime("%Y-%m-%d"):
            print('Remove file: ', nameOfFile)
            os.remove(nameOfFile)

    ## Request for generate tmp file
    def genTmpRepostFile(self):
        GenFolder(self.nameReportFolder)
        fileName = str(datetime.now().strftime("%Y-%m-%d")) + '~' + self.nameReportFile.replace("/", "%") + '.log'
        data = str(datetime.now().strftime("%Y-%m-%d_%H:%M:%S")) + '~' + str(self.testSuiteName) + '~' + str(
            self.testCaseName) + '~' + str(self.duration) + '~' + str(self.testResult) + '\n'
        WriteOpenData(fileName=fileName, folderName=self.nameReportFolder, writeData=data, openType='a')

    # Load tmp report file from report folder
    def genReportFromFolder(self):
        for file in os.listdir(self.nameReportFolder):
            if file.endswith(".log"):
                self.removeLogFileThen(self.nameReportFolder + file)
                testSuite = self.CreateTestSuite(file=file)
        return testSuite

    ## generate junit xml report file
    def genXmlReport(self, TestSuiteData):
        with open(
                self.nameReportFolder + self.nameReportFile + "-" + str(datetime.now().strftime("%Y-%m-%d")) + ".xml",
                'w') as file:
            TestSuite.to_file(file_descriptor=file, test_suites=TestSuiteData, prettyprint=True)

    ## create test suite in junit xml structure
    def CreateTestSuite(self, file):
        testSuites = []
        testCases = []
        with LoadContent(self.nameReportFolder.replace("/", "") + '/', file) as f:
            dataFileContent = f.read()
            linesFileContent = dataFileContent.splitlines()
            previousValueTime = ""
            for index, lineFileContent in enumerate(linesFileContent, start=0):
                splitLine = lineFileContent.split('~')

                if index == 0:
                    previousValueTime = str(splitLine[0])
                if previousValueTime != str(splitLine[0]):
                    testSuites.append(
                        TestSuite(name=self.testSuiteName,
                                  test_cases=testCases,
                                  timestamp=previousValueTime
                                  )
                    )
                    testCases = []
                testCase = self.CreateTestCase(splitLine)
                testCases.append(testCase)
                previousValueTime = splitLine[0]
        return testSuites

    ## create test case in junit xml structure
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
            testCase.add_failure_info(message=result, output=result)
        return testCase


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--ConfFile', required=False, help="This file contains all previous parameters for test",
                        type=str)

    args = parser.parse_args()
    ## Load data from config file
    loadedData = LoadTestData(args)

    for index, config in enumerate(loadedData, start=0):
        if config['request']['method'] == 'POST' and Validator(
                response=config['request']['requestData']).CaseIsJSON() is False:
            print(args)
            print("It is necessary set the parameter 'RequestData' for POST method on valid escape json: \n",
                  args.RequestData
                  )
            exit(1)
        ApiTester(
            endPoint=config['request']['endPoint'],
            methodType=config['request']['method'],
            jsonReq=config['request']['requestData'],
            responseNumber=config['request']['responseStatus'],
            timeoutForAction=config['request']['timeoutForActionSec'],
            responseValidations=config['request']['validationRules'],
            apiNameTestCase=config['request']['nameTestCase'],
            apiNameTestSuite=config['request']['nameTestSuite']
        )
