import json
import os
from modules.resultGenerator import ResultGenerator
from modules.operations import Operations


### Class validate response
class Validator:
    def __init__(self, response, responseValidationRules="", duration=0.0, testSuiteName="", testCaseName="", buildNumber=0):
        self.response = response
        self.duration = duration
        self.testCaseName = testCaseName
        self.testSuiteName = testSuiteName
        self.buildNumber = buildNumber
        responseValidationRules = responseValidationRules.split('~')
        for validationRules in responseValidationRules:
            if "ResponseTimeSec" in validationRules:
                ResponseTimeSec = validationRules.split('=')
                self.CaseResponseReturnTo(float(ResponseTimeSec[1]))
            else:
                getattr(self, 'Case' + validationRules)()

    def CaseSkipRun(self):
        ResultGenerator(
            nameReportFolder="reports/",
            nameReportFile=self.testCaseName,
            testSuiteName=self.testSuiteName,
            testCaseName=self.testCaseName + " - This testcase was skipped",
            testResult=self.response,
            buildNumber=self.buildNumber
        )

    def CaseResponseReturnTo(self, time):
        errorMessage = ''
        if time <= self.duration:
            errorMessage = "FAILURE: The response returns with bigger time. (defined: " + str(
                time) + "sec, actual: " + str(self.duration) + " sec) "
        ResultGenerator(
            nameReportFolder="reports/",
            nameReportFile=self.testCaseName,
            testSuiteName=self.testSuiteName,
            testCaseName=self.testCaseName + " - ResponseReturnTo",
            duration=0.0,
            testResult=errorMessage,
            buildNumber=self.buildNumber
        )

    ## Validator if response come
    def CaseResponseStatus(self):
        errorMessage = ''
        if 'ERROR:' in self.response['text']:
            errorMessage = self.response['text']
        elif 'FAILURE:' in self.response['text']:
            errorMessage = self.response['text']
        ResultGenerator(
            nameReportFolder="reports/",
            nameReportFile=self.testCaseName,
            testSuiteName=self.testSuiteName,
            testCaseName=self.testCaseName + " - Response come with status: " + str(self.response['status_code']),
            duration=self.duration,
            testResult=errorMessage,
            buildNumber=self.buildNumber
        )

    ## Create expected data validation file if not exist
    def CaseCreateResponseFileOutput(self):
        createNewFile = self.testSuiteName.replace("/", "-")
        folderName = "apisResponse/" + createNewFile  # + "/response"
        Operations.GenFolder(folderName)
        Operations.WriteOpenData(fileName=createNewFile + '.json', folderName=folderName,
                                 writeData=self.response['text'],
                                 openType="w")

    ## Validator if data should be same
    def CasePreviousDataValidation(self):
        createNewFile = self.testSuiteName.replace("/", "-")
        folderName = 'apisResponse/' + createNewFile + "/"
        errorMessage = ''
        expectedData = ''
        if os.path.exists(folderName):
            fileLoad = Operations.LoadContent(nameReportFolder=folderName, file=createNewFile + ".json")
            expectedData = fileLoad.read()
        else:
            self.CaseCreateResponseFileOutput()
        if str(self.response['text']) != str(expectedData):
            errorMessage = "FAILURE: The response is not same as expected."
        if expectedData == "":
            errorMessage = "ERROR: Problem with loading file."
        ResultGenerator(
            nameReportFolder="reports/",
            nameReportFile=createNewFile,
            testSuiteName=self.testSuiteName,
            testCaseName=self.testCaseName + " - validateExpectedData",
            duration=0.0,
            testResult=errorMessage,
            buildNumber=self.buildNumber
        )

    ## validate text
    def CaseText(self):
        # TODO: TBD
        print("2")
        return

    ## validate number
    def CaseNumber(self):
        # TODO: TBD
        print("3")
        return

    ##  validate array
    def CaseArray(self):
        # TODO: TBD
        print("4")
        return

    ## validate data in structure
    def CaseCheckValueInStructure(self):
        # TODO: TBD
        print("10")
        return

    ## validate json response
    def CaseParsableJson(self):
        errorMessage = ""
        validator = Validator(response=self.response['text'], responseValidationRules="IsJSON")
        isValidStructure = True
        if 'ERROR:' in self.response['text']:
            print("ERROR: " + self.response['text'])
            errorMessage = self.response['text']
        elif not validator:
            errorMessage = "FAILURE: The response is not in json format."
            isValidStructure = False
        ResultGenerator(
            nameReportFolder="reports/",
            nameReportFile=self.testCaseName,
            testSuiteName=self.testSuiteName,
            testCaseName=self.testCaseName + " - validateJsonStructure",
            duration=0.0,
            testResult=errorMessage,
            buildNumber=self.buildNumber
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
            genXMLReport=True,
            buildNumber=self.buildNumber
        )
        return
    def CaseReturnData(self):
        return
