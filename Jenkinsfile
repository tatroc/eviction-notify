pipeline {
    agent any

    stages {
        stage('test') {
            steps {
                script {
                def n = 3
                n.times {

                     withCredentials([usernamePassword(credentialsId: "${subscription_id}", usernameVariable: 'APP_ID', passwordVariable: 'PASSWORD')]) {
                        sh "az login --service-principal --username ${APP_ID} --password ${PASSWORD} --tenant ${TENANT}"
                        sh "az account set --subscription ${subscription_id}"
                        sh "az vm start -g ${resource_group} -n ${name}"
                     }
                    sleep(15)
                }
                }
            }
        }
    
    }
}