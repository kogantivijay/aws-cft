properties([
    parameters([
        extendedChoice(
            name: 'TARGET_PRODUCTS',
            type: 'PT_CHECKBOX',
            defaultValue: 'ProductA',
            multiSelectDelimiter: ',',
            value: 'ProductA,ProductB,ProductC',
            description: 'Select the products to deploy'
        )
    ])
])

pipeline {
    agent any
    stages {
        stage('SCM Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Deployment') {
            steps {
                script {
                    // Split the TARGET_PRODUCTS parameter to get a list of products
                    def products = params.TARGET_PRODUCTS.split(',')

                    // Get the target environment from the environment variable
                    def environment = env.TARGET_ENV

                    // Define a map to hold the deployment tasks
                    def deployments = [:]

                    // Iterate over each product and deploy
                    for (product in products) {
                        // Add the deployment task to the map
                        deployments["${product.trim()}-${environment}"] = {
                            // Deployment logic here...
                            echo "Deploying product ${product.trim()} to environment ${environment}"
                        }
                    }

                    // Execute deployments in parallel
                    parallel deployments
                }
            }
        }
    }
    post {
        always {
            cleanWs()
        }
    }
}
