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
        stage('CR number validation') {
            when {
                expression { params.TARGET_ENV.toLowerCase().contains('pdn') }
            }
            steps {
                script {
                    def validCRNumberRegex = ~/^CHG\d{10}$/
                    // If CR number is invalid or default, ask for user input
                    if (!params.CR_NUMBER_PROD.matches(validCRNumberRegex)) {
                        params.CR_NUMBER_PROD = promptForCRNumber(validCRNumberRegex)
                    }
                }
            }
        }

def promptForCRNumber(validCRNumberRegex) {
    def userInput = input message: 'CR number for Prod deployment is invalid or default. Please provide a valid CR number:',
        id: 'crNumberInput',
        ok: 'Proceed',
        parameters: [
            string(
                defaultValue: '', 
                description: 'CR Number for Prod Deployment', 
                name: 'CR_Number', 
                trim: true
            )
        ]

    while (!userInput.CR_Number.matches(validCRNumberRegex)) {
        userInput = input message: 'CR number for Prod deployment is invalid. Please provide a valid CR number:',
            id: 'crNumberInput',
            ok: 'Proceed',
            parameters: [
                string(
                    defaultValue: '', 
                    description: 'CR Number for Prod Deployment', 
                    name: 'CR_Number', 
                    trim: true
                )
            ]
    }
    return userInput.CR_Number
}

        


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
