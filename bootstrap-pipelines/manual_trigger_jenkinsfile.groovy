// Jenkinsfile
@Library('deployUtils') _

pipeline {
    agent any
    parameters {
        extendedChoice(name: 'PRODUCTS', choices: ['ProductA', 'ProductB'], description: 'Choose products to deploy', multiSelectDelimiter: ',', type: 'PT_CHECKBOX')
        extendedChoice(name: 'ENVIRONMENTS', choices: ['Dev', 'Test', 'Prod'], description: 'Choose environments to deploy to', multiSelectDelimiter: ',', type: 'PT_CHECKBOX')
    }
    stages {
        stage('Manual Deployment') {
            steps {
                script {
                    // Split the selected products and environments into arrays
                    def selectedProducts = params.PRODUCTS.split(',')
                    def selectedEnvironments = params.ENVIRONMENTS.split(',')
                    
                    // Prepare a map for parallel execution
                    def deployments = [:]
                    for (product in selectedProducts) {
                        for (environment in selectedEnvironments) {
                            // Each deployment is added to the map as a closure
                            deployments["$product-$environment"] = {
                                deploy(product, environment)
                            }
                        }
                    }

                    // Execute deployments in parallel
                    parallel deployments
                }
            }
        }
    }
}
