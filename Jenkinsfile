pipeline {
    agent any

    environment {
        // Points Jenkins to the Minikube configuration directory
        KUBECONFIG = '/var/lib/jenkins/.kube/config'
        MINIKUBE_HOME = '/var/lib/jenkins'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out application source code'
                checkout scm
            }
        }

        stage('Build') {
            steps {
                echo 'Building Docker images'
                sh '''
                    docker build -t iris-backend:1.0 ./backend
                    docker build -t iris-frontend:1.0 ./frontend
                '''
            }
        }

        stage('Test') {
            steps {
                echo 'Testing application files'
                sh '''
                    python3 -m py_compile backend/app.py
                    test -f frontend/index.html
                    test -f k8s/deployment.yaml
                '''
            }
        }

        stage('Deploy') {
    steps {
        echo 'Loading Docker images into Minikube'

        sh '''
            minikube image load iris-backend:1.0
            minikube image load iris-frontend:1.0
        '''

        echo 'Deploying application to Kubernetes'

        sh '''
            export KUBECONFIG=/var/lib/jenkins/.kube/config

            kubectl apply -f k8s/deployment.yaml
        '''
        }
      }
    }

    post {
        success {
            echo 'CI/CD Pipeline succeeded!'
        }
        failure {
            echo 'CI/CD Pipeline failed. Check the console output.'
        }
    }
}
