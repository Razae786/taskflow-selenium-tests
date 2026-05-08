pipeline {
    agent {
        label 'agent1'
    }
    
    options {
        timeout(time: 10, unit: 'MINUTES')
        disableConcurrentBuilds()
    }
    
    stages {
        stage('Deploy Taskflow App') {
            steps {
                sh '''
                    cd /home/ubuntu/Taskflow
                    docker compose down 2>/dev/null || true
                    docker compose up -d
                    sleep 15
                    curl -s http://localhost:3000 > /dev/null && echo "App ready"
                '''
            }
        }
        
        stage('Install Test Dependencies') {
            steps {
                sh '''
                    sudo apt-get update
                    sudo apt-get install -y google-chrome-stable chromium-browser chromium-chromedriver || true
                    pip3 install selenium pytest pytest-html webdriver-manager --break-system-packages
                '''
            }
        }
        
        stage('Run Selenium Tests') {
            steps {
                sh '''
                    cd /home/ubuntu/taskflow-selenium-tests
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
                def results = sh(script: "cat results/test-output.txt 2>/dev/null || echo 'No output'", returnStdout: true).trim()
                
                emailext(
                    to: "${committer}, qasimalik@gmail.com",
                    subject: "Taskflow Tests - Build #${env.BUILD_NUMBER}",
                    body: """
Build #${env.BUILD_NUMBER}
Triggered by: ${committer}

Results:
${results}

App: http://16.54.195.112:3000
Build: ${env.BUILD_URL}
"""
                )
            }
        }
    }
}
