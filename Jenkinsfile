pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                git credentialsId: 'github-ssh', url: 'git@github.com:woletokun/idp.git', branch: 'main'
            }
        }
        stage('Build Image') {
            steps {
                script {
                    docker.build("woletokun/idp:${env.BUILD_NUMBER}")
                }
            }
        }
        stage('Push Image') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'USER', passwordVariable: 'PASS')]) {
                    sh "docker login -u $USER -p $PASS"
                    sh "docker push woletokun/idp:${env.BUILD_NUMBER}"
                }
            }
        }
        stage('Update Manifests') {
            steps {
                sh """
                sed -i 's|image: .*|image: woletokun/idp:${env.BUILD_NUMBER}|' k8s/deployment.yaml
                git config --global user.email "ci@jenkins"
                git config --global user.name "jenkins"
                git add k8s/deployment.yaml
                git commit -m "Update image to build ${env.BUILD_NUMBER}"
                git push origin main
                """
            }
        }
    }
}
