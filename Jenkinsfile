pipeline {
    agent any

    environment {
        APP_HOST = '192.168.1.2'
        APP_USER = '<USER>'   // замените на ваше имя пользователя
        APP_PATH = "/home/${APP_USER}/web-service-ha-lab"
    }

    stages {
        stage('Sync code to App Server') {
            steps {
                script {
                    sh """
                        ssh ${APP_USER}@${APP_HOST} "
                            cd ${APP_PATH} && git pull || echo 'no git'
                        "
                    """
                }
            }
        }

        stage('Deploy via Docker Compose') {
            steps {
                script {
                    sh """
                        ssh ${APP_USER}@${APP_HOST} "
                            cd ${APP_PATH} &&
                            docker-compose down --remove-orphans &&
                            docker-compose up -d --build
                        "
                    """
                }
            }
        }

        stage('Health Check') {
            steps {
                script {
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
            script {
                echo "Health check FAILED! Rolling back..."
                sh """
                    ssh ${APP_USER}@${APP_HOST} "
                        cd ${APP_PATH} &&
                        docker-compose up -d --no-build
                    "
                """
            }
        }
        success {
            echo "Deployment successful!"
        }
    }
}
