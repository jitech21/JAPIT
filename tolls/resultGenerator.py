from junit_xml import TestSuite, TestCase
from datetime import datetime
from tolls.operations import Operations
import os


## junit XML report
class ResultGenerator:

    def __init__(self, nameReportFolder, nameReportFile, testSuiteName, testCaseName, testResult,
                 genXMLReport=False, duration=0.0, buildNumber=0):
        self.parsedResult = None
        self.testSuiteName = testSuiteName
        self.testCaseName = testCaseName
        self.duration = duration
        self.testResult = testResult
        self.nameReportFolder = nameReportFolder
        self.nameReportFile = ""
        if genXMLReport:
            self.genXmlReport(self.genReportFromFolder())
        else:
            self.genTmpRepostFile(buildNumber)

    ## Remove unused file
    def removeLogFileThen(self, nameOfFile):
        now = datetime.now()
        parsedDateName = nameOfFile.replace('.log', '')
        parsedDateName = parsedDateName.replace('reports/', '')
        parsedDateName = parsedDateName.split('~')
        if parsedDateName[0] < now.strftime("%Y-%m-%d"):
            os.remove(nameOfFile)
            print('Remove file: ', nameOfFile)
            return True
        return False

    ## Request for generate tmp file
    def genTmpRepostFile(self, buildNumber=0):
        Operations.GenFolder(self.nameReportFolder)
        errorMessage = ''
        if 'ERROR:' in self.testResult:
            errorMessage = self.testResult
        elif 'FAILURE:' in self.testResult:
            errorMessage = self.testResult
        elif 'DISABLED:' in self.testResult:
            errorMessage = self.testResult
        # name of temp file log _%H:%M
        fileName = str(datetime.now().strftime("%Y-%m-%d")) + '~' + str(buildNumber) + '.log'
        data = str(datetime.now().strftime("%Y-%m-%d_%H:%M:%S")) + '~' + str(self.testSuiteName) + '~' + str(
            self.testCaseName) + '~' + str(self.duration) + '~' + str(errorMessage) + '\n'
        Operations.WriteOpenData(fileName=fileName, folderName=self.nameReportFolder, writeData=data, openType='a')

    # Load tmp report file from report folder
    def genReportFromFolder(self):
        for file in os.listdir(self.nameReportFolder):
            self.nameReportFile = file.replace('.log', '.xml')
            testSuite = []
            if file.endswith(".log"):
                if not self.removeLogFileThen(self.nameReportFolder + file):
                    testSuite = self.CreateTestSuite(file=file)
                return testSuite

    ## generate junit xml report file
    def genXmlReport(self, TestSuiteData):
        filename = self.nameReportFile.replace("/", "-")
        with open(
                self.nameReportFolder + filename,
                'w') as file:
            TestSuite.to_file(file_descriptor=file, test_suites=TestSuiteData, prettyprint=True)

    ## create test suite in junit xml structure
    def CreateTestSuite(self, file):
        testSuites = []
        testCases = []
        with Operations.LoadContent(self.nameReportFolder, file) as f:
            dataFileContent = f.read()
            linesFileContent = dataFileContent.splitlines()
            previousValueNameSuite = ""
            previousValueTime = ""
            for index, lineFileContent in enumerate(linesFileContent, start=0):
                splitLine = lineFileContent.split('~')
                if index == 0:
                    previousValueTime = str(splitLine[0])
                if previousValueTime != str(splitLine[0]):
                    testSuites.append(
                        TestSuite(name=previousValueNameSuite,
                                  test_cases=testCases,
                                  timestamp=previousValueTime
                                  )
                    )
                    testCases = []
                testCase = self.CreateTestCase(splitLine)
                testCases.append(testCase)
                testCase = []
                previousValueTime = splitLine[0]
                previousValueNameSuite = self.testSuiteName
            testSuites.append(
                TestSuite(name=self.testSuiteName,
                          test_cases=testCases,
                          timestamp=previousValueTime
                          )
            )
        return testSuites

    ## create test case in junit xml structure
    def CreateTestCase(self, parsedResult):
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