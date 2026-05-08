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
        
        stage('Install Chrome & Dependencies') {
            steps {
                sh '''
                    sudo apt-get update
                    sudo apt-get install -y google-chrome-stable chromium-browser chromium-chromedriver || true
                    pip3 install selenium pytest pytest-html webdriver-manager --break-system-packages
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
            }
        }
    }
    
    post {
        always {
            script {
                def committer = sh(script: "git log -1 --pretty=format:'%ae'", returnStdout: true).trim()
                def results = sh(script: "cat results/test-output.txt 2>/dev/null || echo 'No results'", returnStdout: true).trim()
                
                emailext(
                    to: "${committer}, qasimalik@gmail.com",
                    subject: "Taskflow Selenium Tests - Build #${env.BUILD_NUMBER}",
                    body: """
Test Results for Taskflow
=========================
Build: #${env.BUILD_NUMBER}
URL: ${env.BUILD_URL}

${results}
"""
                )
            }
        }
    }
}
