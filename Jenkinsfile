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
                    # Remove broken Google repo if it was added previously
                    sudo rm -f /etc/apt/sources.list.d/google.list /etc/apt/sources.list.d/google-chrome.list
                    
                    # Install Chromium from Ubuntu repos (already available)
                    sudo apt-get update
                    sudo apt-get install -y chromium-browser chromium-chromedriver || true
                    
                    # Install Python test dependencies
                    pip3 install selenium==4.25.0 pytest==7.4.0 pytest-html==4.1.1 --break-system-packages
                    
                    # Verify
                    chromedriver --version || echo "chromedriver not found but continuing"
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                sh '''
                    export PATH=$PATH:/home/ubuntu/.local/bin
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
                def results = sh(script: "cat results/test-output.txt 2>/dev/null || echo 'No test output'", returnStdout: true).trim()
                
                emailext(
                    to: "${committer}, qasimalik@gmail.com",
                    subject: "Taskflow Selenium Tests - Build #${env.BUILD_NUMBER}",
                    body: """
Test Results for Taskflow
=========================
Build: #${env.BUILD_NUMBER}
Triggered by: ${committer}

${results}

Build URL: ${env.BUILD_URL}
"""
                )
            }
        }
    }
}
