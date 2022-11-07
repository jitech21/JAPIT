// Global variable
import java.text.SimpleDateFormat
def dateFormat = new SimpleDateFormat("yyyy-MM-dd")
def date = new Date()
def timestamp = dateFormat.format(date)
def buildNumber = currentBuild.number
String[] RunParamters = []
CurrentErrors = 0
if (params.Configurations != '')
{
    RunParamters = params.Configurations.replace(':selected','').split(',')
}
// TODO: create this file in the workspace
stage(String.format('Clone Git')){
    node{
        echo 'Clone Git'
        // change if possible
        git branch: 'main', url: 'https://github.com/jitech21/apiTEster.git'
        // echo 'Git pull'
        // sh 'git pull'
        // echo 'Git fetch'
        // sh 'git fetch'

    }
}
for (configuration in RunParamters)
{
    stage(String.format('Api Test: %s', configuration)){
        //parallel (
            catchError{
                node{
                    try {
                        echo String.format('Test API: %s', configuration )
                        echo 'RUN SCRIPT'
                        echo 'python apiTester.py --BuildNumber '+buildNumber + ' --ConfFile "'+configuration+'"'
                        sh 'python apiTester.py --BuildNumber '+buildNumber + ' --ConfFile "'+configuration+'"'
                    } catch (e) {
                        currentBuild.result = "Connection detection: "+configuration+" - FAILED"
                        notifyFailed(configuration)
                        CurrentErrors = CurrentErrors+1
                        throw e
                    }
                }
            }
        // )
    }
}
stage('Reports') {
    node {
        catchError(buildResult: 'UNSTABLE', stageResult: 'SUCCESS') {
            // echo String.format('Current error/s: %s', CurrentErrors )
            echo 'reports/'+timestamp+'~'+buildNumber+'.xml'
            junit keepLongStdio: true, skipPublishingChecks: true, testResults: 'reports/'+timestamp+'~'+buildNumber+'.xml'
            if(CurrentErrors == 0){
              currentBuild.result = 'SUCCESS'
            } else if(currentBuild.result == 'UNSTABLE'){
              currentBuild.result = 'SUCCESS'
            } else {
              currentBuild.result = 'ERROR'
            }
        }
    }
}

def notifyFailed(domain) {
    emailext (
        to: 'jitech@jitech.cz',
        subject: "FAILED: API Job '${env.JOB_NAME} - ${env.BUILD_NUMBER}'",
        mimeType: 'text/html',
        body: """<p>FAILED: Job #${env.JOB_NAME} - ${env.BUILD_NUMBER} for domain: '${domain}'</p>
            <p>Check console output at (<a href='${env.BUILD_URL}'>${env.JOB_NAME} - [${env.BUILD_NUMBER}]</a>)</p>""",
        replyTo: '$DEFAULT_REPLYTO'
    )
}
def notifySuccessful(domain) {
    emailext (
        to: 'jitech@jitech.cz',
        subject: "SUCCESSFUL: API Job '${env.JOB_NAME} - ${env.BUILD_NUMBER}'",
        mimeType: 'text/html',
        body: """<p>SUCCESSFUL: Job #${env.JOB_NAME} - [${env.BUILD_NUMBER}] for domain: ${domain}</p>
            <p>Check console output at (<a href='${env.BUILD_URL}'>${env.JOB_NAME} - ${env.BUILD_NUMBER}</a>)</p>""",
        replyTo: '$DEFAULT_REPLYTO'
        )
}