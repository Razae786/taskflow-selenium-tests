pipeline {
    agent {
        label 'agent1'
    }
    
    options {
        timeout(time: 10, unit: 'MINUTES')
        disableConcurrentBuilds()
    }
    
    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/Razae786/taskflow-selenium-tests.git'
            }
        }
        
        stage('Run Tests in Docker Container') {
            steps {
                sh '''
                    # Ensure Docker image is available
                    docker pull selenium/standalone-chrome:120.0
                    
                    # Run tests inside Docker container using plain docker run
                    # The container needs python3, pip, and pytest installed
                    docker run --rm \
                        -v $(pwd):/tests \
                        -w /tests \
                        --shm-size=2g \
                        --network=host \
                        --entrypoint="" \
                        selenium/standalone-chrome:120.0 \
                        bash -c "
                            apt-get update -qq && apt-get install -y -qq python3 python3-pip > /dev/null 2>&1
                            pip3 install -q selenium==4.25.0 pytest==7.4.0 pytest-html==4.1.1
                            mkdir -p results
                            python3 -m pytest tests/test_taskflow.py \
                                --junitxml=results/test-results.xml \
                                --html=results/report.html \
                                -v --tb=short 2>&1 | tee results/test-output.txt || true
                        "
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
