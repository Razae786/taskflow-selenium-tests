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
                    # Force remove ALL Google repo files
                    sudo rm -f /etc/apt/sources.list.d/google*.list
                    sudo rm -f /etc/apt/sources.list.d/*google*
                    
                    # Clean apt cache for broken repos
                    sudo rm -rf /var/lib/apt/lists/partial/*
                    
                    # Update with allow-insecure to skip broken repos
                    sudo apt-get update --allow-insecure-repositories || sudo apt-get update || true
                    
                    # Install Chromium from Ubuntu repos
                    sudo apt-get install -y chromium-browser chromium-chromedriver || true
                    
                    # Install Python dependencies
                    pip3 install selenium==4.25.0 pytest==7.4.0 pytest-html==4.1.1 --break-system-packages
                    
                    # Verify
                    which chromedriver || echo "chromedriver not in PATH"
                    which chromium-browser || which chromium || echo "chromium not found"
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
                    to: "${committer}",
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
