pipeline {
    agent {
        label 'agent1'
    }
    
    options {
        timeout(time: 5, unit: 'MINUTES')
        disableConcurrentBuilds()
    }
    
    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/Razae786/taskflow-selenium-tests.git'
            }
        }
        
        stage('Install Chrome & Drivers') {
            steps {
                sh '''
                    sudo apt-get update
                    sudo apt-get install -y google-chrome-stable chromium-browser chromium-chromedriver || true
                    pip3 install selenium==4.25.0 pytest==7.4.0 pytest-html==4.1.1 webdriver-manager==4.0.1 --break-system-packages
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                sh '''
                    mkdir -p results
                    python3 -m pytest tests/test_taskflow.py \
                        --junitxml=results/test-results.xml \
                        --html=results/report.html \
                        -v --tb=short 2>&1 | tee results/test-output.txt || true
                '''
            }
        }
        
        stage('Publish Results') {
            steps {
                junit 'results/test-results.xml'
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'results',
                    reportFiles: 'report.html',
                    reportName: 'Selenium Test Report'
                ])
            }
        }
    }
    
    post {
        always {
            script {
                def committerEmail = sh(script: "git log -1 --pretty=format:'%ae'", returnStdout: true).trim()
                def committerName = sh(script: "git log -1 --pretty=format:'%an'", returnStdout: true).trim()
                def results = sh(script: "cat results/test-output.txt 2>/dev/null || echo 'No test output available'", returnStdout: true).trim()
                def buildStatus = currentBuild.currentResult ?: 'UNKNOWN'
                
                emailext(
                    subject: "${env.JOB_NAME} - Build #${env.BUILD_NUMBER} - ${buildStatus}",
                    body: """
Build Notification
==================
Project: ${env.JOB_NAME}
Build Number: #${env.BUILD_NUMBER}
Status: ${buildStatus}
Triggered By: ${committerName} <${committerEmail}>
Build URL: ${env.BUILD_URL}

Test Results:
${results}

---
This is an automated message from Jenkins.
""",
                    to: "${committerEmail}, razaeilyas123@gmail.com",
                    from: "jenkins@taskflow-ci.com",
                    replyTo: "razaeilyas123@gmail.com",
                    mimeType: 'text/plain'
                )
            }
        }
        
        failure {
            script {
                def committerEmail = sh(script: "git log -1 --pretty=format:'%ae'", returnStdout: true).trim()
                emailext(
                    subject: "FAILED: ${env.JOB_NAME} - Build #${env.BUILD_NUMBER}",
                    body: "Build FAILED. Check logs at: ${env.BUILD_URL}console",
                    to: "${committerEmail}, razaeilyas123@gmail.com",
                    from: "jenkins@taskflow-ci.com"
                )
            }
        }
    }
}
