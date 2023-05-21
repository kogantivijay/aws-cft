pipeline {
    agent any
    stages {
        stage('Input parameters') {
            steps {
                script {
                    properties([
                        parameters([
                            choice(name: 'Environment', 
                                   choices: ['Dev', 'Stage', 'Prod'], 
                                   description: 'Please select the environment'),
                            string(name: 'changeRef', 
                                   defaultValue: '', 
                                   description: 'Change reference', 
                                   trim: true),
                            string(name: 'lctRef', 
                                   defaultValue: '', 
                                   description: 'LCT reference', 
                                   trim: true),
                            extendedChoice(name: 'PRODUCTS_LIST', 
                                           type: 'PT_CHECKBOX', 
                                           multiSelectDelimiter: ',', 
                                           quoteValue: false, 
                                           saveJSONParameterToFile: false, 
                                           visibleItemCount: 5, 
                                           groovyScript: 'return["Product1", "Product2", "Product3"]')
                        ])
                    ])
                }
                script {
                    def productsList = params.PRODUCTS_LIST.split(',')
                    for (product in productsList) {
                        // Do something with each product
                        echo "Selected product: ${product}"
                    }
                }
            }
        }
    }
}
