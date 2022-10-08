'''
API testing tool
'''

# TODO: implement requests
# TODO: retest all type of requests
# TODO: validation of reponse
## TODO: Json structure
## TODO: validate keys
## TODO: validate type of value in define keys
# TODO: authentication via OATH2.0
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
    def __init__(self, response, responseFormat, expectedValues="", duration=0.0, testSuiteName="", testCaseName=""):
        self.response = response
        self.expectedValues = expectedValues
        self.duration = duration
        self.testCaseName = testCaseName
        self.testSuiteName = testSuiteName
        getattr(self, 'Case' + responseFormat)()

    def CaseJson(self):
        self.CaseJsonStructure()
        

    def CaseText(self):
        # TODO: TBD
        print("2")

    def CaseNumber(self):
        # TODO: TBD
        print("3")

    def CaseArray(self):
        # TODO: TBD
        print("4")

    def CaseJsonStructure(self):
        errorMessage = ""
        validator = Validator(response=self.response, responseFormat="IsJSON")
        if self.response.startswith("ERROR:"):
            errorMessage = self.response
        elif not validator.CaseIsJSON():
            errorMessage = "FAILURE: The response is not in json format. \n", self.response

        ResultGenerator(
            nameReportFolder="reports/",
            nameReportFile=self.testCaseName,
            testSuiteName=self.testSuiteName,
            testCaseName=self.testCaseName,
            duration=self.duration,
            testResult=errorMessage
        )
        return

    def CaseIsJSON(self):
        try:
            json.loads(self.response)
        except ValueError as e:
            print('invalid json: %s' % e)
            return None
        return True


class ResultGenerator:

    def __init__(self, nameReportFolder, nameReportFile, testSuiteName, testCaseName, duration, testResult, genXMLReport = False):
        if genXMLReport:
            self.genXmlReport(self.genReportFromFolder())
            return
        self.parsedResult = None
        self.testSuiteName = testSuiteName
        self.testCaseName = testCaseName
        self.duration = duration
        self.testResult = testResult
        self.nameReportFolder = nameReportFolder
        self.nameReportFile = nameReportFile
        self.genTmpRepostFile()

    def removeLogFileThen(self, nameOfFile):
        now = datetime.now()
        parsedDateName = nameOfFile.replace('~' + self.nameReportFile.replace("/", "%") + '.log', '')
        parsedDateName = parsedDateName.replace('reports/','')
        print('Remove file: ', parsedDateName)

        if parsedDateName < now.strftime("%Y-%m-%d"):
            print('Remove file: ', nameOfFile)
            os.remove(nameOfFile)

    def genTmpRepostFile(self):
        self.genFolder()
        file = open(
            self.nameReportFolder +
            str(datetime.today().strftime("%Y-%m-%d")) +
            '~'
            + self.nameReportFile.replace("/", "%") + '.log',
            "a"
        )
        file.write(
            str(datetime.today().strftime("%Y-%m-%d_%H:%m:%S")) +
            '~' + str(self.testSuiteName) +
            '~' + str(self.testCaseName) +
            '~' + str(self.duration) +
            '~' + str(self.testResult) + '\n'
        )
        file.close()

    def genReportFromFolder(self):
        testSuite = []
        for file in os.listdir(self.nameReportFolder):
            if file.endswith(".log"):
                self.removeLogFileThen(self.nameReportFolder + file)
                testSuite.append(
                    self.CreateTestSuite(file=file)
                )
        return testSuite

    def genXmlReport(self, TestSuiteData):
        with open(
                self.nameReportFolder + self.nameReportFile + "-" + str(datetime.today().strftime("%Y-%m-%d")) + ".xml",
                'w') as file:
            TestSuite.to_file(file_descriptor=file, test_suites=TestSuiteData, prettyprint=True)

    def CreateTestSuite(self, file):
        return TestSuite(name=self.testSuiteName,
                         test_cases=self.CreateTestCases(file),
                         timestamp=str(datetime.today().strftime("%Y-%m-%d"))
                         )

    def CreateTestCases(self, file):
        testCases = []
        with open(self.nameReportFolder.replace("/", "") + '/' + file, 'r') as f:
            dataFileContent = f.read()
            linesFileContent = dataFileContent.splitlines()
            for lineFileContent in linesFileContent:
                testCases.append(
                    self.createTestCase(parsedResult=lineFileContent.split('~'))
                )
        return testCases

    def createTestCase(self, parsedResult, testCases=None):
        testCase = TestCase(
            name=parsedResult[2],
            elapsed_sec=float(parsedResult[3])
        )
        result = parsedResult[4]
        if result.startswith('ERROR:'):
            testCase.add_error_info(message=result, output=result)
        elif result.startswith('DISABLED:'):
            testCase.add_skipped_info(message=result, output=result)
        elif result.startswith('FAILURE:'):
            testCase.add_failure_info(message=result, output=result)
        return testCase

    def genFolder(self):
        if not os.path.exists(self.nameReportFolder):
            os.mkdir(self.nameReportFolder)
            print("Directory ", self.nameReportFolder, " Created ")
        return


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
                        help="ResponseFormat which type of response should be expected. types: (Text, Number, Json, Array, JsonStructure)",
                        type=str
                        )
    parser.add_argument('--ApiNameTestCase', required=True,
                        help="ApiNameTestCase name of test case",
                        type=str
                        )
    parser.add_argument('--ApiNameTestSuite', required=True,
                        help="ApiNameTestSuite name of test case",
                        type=str
                        )

    args = parser.parse_args()
    if args.MethodType == 'POST' and Validator(response=args.RequestData, responseFormat="caseIsJSON") is False:
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
