// Jenkinsfile
@Library('deployUtils') _

pipeline {
    agent any
    stages {
        stage('Determine Deployment Scope') {
            steps {
                script {
                    // Get a list of modified files
                    def modifiedFiles = sh(script: 'git diff --name-only HEAD^..HEAD', returnStdout: true).trim().split('\n')

                    // Determine which products and environments were modified
                    def modifiedProducts = []
                    def modifiedEnvironments = []
                    for (file in modifiedFiles) {
                        def parts = file.split('/')
                        if (parts.size() == 2) {
                            // The file is in a product directory
                            def product = parts[0]
                            if (!modifiedProducts.contains(product)) {
                                modifiedProducts.add(product)
                            }
                        } else if (parts.size() == 3) {
                            // The file is in an environment directory
                            def product = parts[0]
                            def environment = parts[1]
                            if (!modifiedProducts.contains(product)) {
                                modifiedProducts.add(product)
                            }
                            if (!modifiedEnvironments.contains(environment)) {
                                modifiedEnvironments.add(environment)
                            }
                        }
                    }

                    // Prepare a map for parallel execution
                    def deployments = [:]
                    for (product in modifiedProducts) {
                        for (environment in modifiedEnvironments) {
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
