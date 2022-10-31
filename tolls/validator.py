import json
import os
from tolls.resultGenerator import ResultGenerator
from tolls.operations import Operations

### Class validate response
class Validator:
    def __init__(self, response, responseValidationRules="", duration=0.0, testSuiteName="", testCaseName=""):
        self.response = response
        self.duration = duration
        self.testCaseName = testCaseName
        self.testSuiteName = testSuiteName
        responseValidationRules = responseValidationRules.split('~')
        if len(responseValidationRules) == 1:
            getattr(self, 'Case' + responseValidationRules[0])()
        else:
            for validationRules in responseValidationRules:
                getattr(self, 'Case' + validationRules)()

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
            testResult=errorMessage
        )

    ## Create expected data validation file if not exist
    def CaseCreateResponseFileOutput(self):
        createNewFile = self.testSuiteName.replace("/", "-")
        folderName = "apisResponse/" + createNewFile  # + "/response"
        Operations.GenFolder(folderName)
        Operations.WriteOpenData(fileName=createNewFile + '.json', folderName=folderName, writeData=self.response['text'],
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
            testResult=errorMessage
        )

    # skip internal validation serve the content in return
    def CaseSkipValidation(self):
        return json.loads(self.response['text'])['access_token']

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
            errorMessage = self.response['text']
        elif not validator.CaseIsJSON():
            errorMessage = "FAILURE: The response is not in json format."
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
        return