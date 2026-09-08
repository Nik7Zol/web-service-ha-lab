pipeline {
    agent any

    environment {
        APP_HOST = '192.168.1.2'
        APP_USER = 'app'                     // замените на ваше имя пользователя на App-сервере
        APP_PATH = "/home/${APP_USER}/web-service-ha-lab"
        SSH_CRED = 'app-server-ssh'          // ID ваших SSH-учётных данных в Jenkins
    }

    stages {
        // Подготовка хоста: установка Docker, Compose, Git и curl
        stage('Prepare Host Environment') {
            steps {
                sshagent([SSH_CRED]) {
                    sh """
                        ssh ${APP_USER}@${APP_HOST} "
                            echo '=== Updating package list ==='
                            sudo apt update -qq

                            echo '=== Installing / checking required utilities ==='

                            if ! command -v docker &> /dev/null; then
                                echo 'Docker not found. Installing...'
                                sudo apt install -y docker.io
                            else
                                echo 'Docker already installed.'
                            fi

                            if ! command -v docker-compose &> /dev/null; then
                                echo 'Docker Compose not found. Installing...'
                                sudo apt install -y docker-compose
                            else
                                echo 'Docker Compose already installed.'
                            fi

                            if ! command -v git &> /dev/null; then
                                echo 'Git not found. Installing...'
                                sudo apt install -y git
                            else
                                echo 'Git already installed.'
                            fi

                            if ! command -v curl &> /dev/null; then
                                echo 'Curl not found. Installing...'
                                sudo apt install -y curl
                            else
                                echo 'Curl already installed.'
                            fi

                            
                            sudo usermod -aG docker ${APP_USER}
                            echo '=== Host preparation completed ==='
                        "
                    """
                }
            }
        }

        // Копирование кода на App-сервер (через SCP)
        stage('Sync code to App Server') {
            steps {
                script {
                    sh """
                        ssh -o StrictHostKeyChecking=no ${APP_USER}@${APP_HOST} "rm -rf ${APP_PATH} && mkdir -p ${APP_PATH}"
                        scp -r ${WORKSPACE}/* ${APP_USER}@${APP_HOST}:${APP_PATH}/
                    """
                }
            }
        }

        // Деплой через Docker Compose (без sudo, через sg docker)
        stage('Deploy via Docker Compose') {
            steps {
                sshagent([SSH_CRED]) {
                    sh """
                        ssh ${APP_USER}@${APP_HOST} "
                            cd ${APP_PATH} &&
                            sg docker -c 'docker-compose down --remove-orphans && docker-compose up -d --build'
                        "
                    """
                }
            }
        }

        // Проверка здоровья приложения
        stage('Health Check') {
            steps {
                sshagent([SSH_CRED]) {
                    sh """
                        ssh ${APP_USER}@${APP_HOST} "
                            sleep 10 &&
                            curl -s -o /dev/null -w '%{http_code}' http://localhost/health | grep 200
                        "
                    """
                }
            }
        }
    }

    post {
        failure {
            echo " Health check FAILED! Rolling back to previous version"
            sshagent([SSH_CRED]) {
                sh """
                    ssh ${APP_USER}@${APP_HOST} "
                        cd ${APP_PATH} &&
                        sg docker -c 'docker-compose up -d --no-build'
                    "
                """
            }
        }
        success {
            echo "Deployment successful!"
        }
    }
}
