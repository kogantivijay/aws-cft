// Jenkinsfile
pipeline {
    agent any
    parameters {
        string(name: 'BRANCH', defaultValue: 'master', description: 'Branch to checkout')
        choice(name: 'TARGET_PRODUCTS', choices: ['ProductA', 'ProductB', 'ProductC'], description: 'Choose products to deploy')
        string(name: 'TARGET_ENV', defaultValue: 'Dev', description: 'Target environment')
    }
    stages {
        stage('Checkout') {
            steps {
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: "${params.BRANCH}"]],
                    doGenerateSubmoduleConfigurations: false,
                    extensions: [],
                    submoduleCfg: [],
                    userRemoteConfigs: [[url: 'https://path/to/your/repo.git']]
                ])
            }
        }
        stage('Determine Deployment Scope') {
            steps {
                script {
                    // Split the products parameter into a list
                    def targetProducts = params.TARGET_PRODUCTS.split(',')

                    // Deploy the chosen products to the chosen environment
                    def deployments = [:]
                    for (product in targetProducts) {
                        deployments["Deploying ${product}"] = {
                            stage("Deploy ${product}") {
                                echo "Deploying product ${product} to environment ${params.TARGET_ENV}"
                                // Deployment logic goes here...
                            }
                        }
                    }
                    parallel deployments
                }
            }
        }
    }
}
