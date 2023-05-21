pipeline {
    agent any
    parameters {
        activeChoiceParam('ENVIRONMENT', 'PT_DROPDOWN', [
            choice(name: 'Dev', value: 'dev'),
            choice(name: 'Stage', value: 'stage'),
            choice(name: 'Prod', value: 'prod')
        ])
        activeChoiceParam('PRODUCTS_LIST', 'PT_CHECKBOX', [
            choice(name: 'Loading options...', value: '')
        ])
        stringParam('changeRef', '')
        stringParam('lctRef', '')
    }
    stages {
        stage('Generate Products List') {
            steps {
                script {
                    // Fetch dynamic product options based on some logic or external source
                    def dynamicProductOptions = fetchDynamicProductOptions()

                    // Update the PRODUCTS_LIST parameter options with the fetched values
                    updateProductOptions(dynamicProductOptions)
                }
            }
        }
        stage('Build') {
            steps {
                script {
                    def environment = params.ENVIRONMENT
                    def productsList = params.PRODUCTS_LIST.split(',')
                    def changeRef = params.changeRef
                    def lctRef = params.lctRef

                    // Use the parameter values in your pipeline logic
                    echo "Environment: ${environment}"
                    echo "Selected Products: ${productsList}"
                    echo "Change Ref: ${changeRef}"
                    echo "LCT Ref: ${lctRef}"

                    // Add your actual build and deployment steps here
                }
            }
        }
    }
}

def fetchDynamicProductOptions() {
    // Implement your logic to fetch dynamic product options, e.g., from an API, database, or file
    return ["ProductA", "ProductB", "ProductC"]
}

def updateProductOptions(options) {
    def paramDef = build job: "${env.JOB_NAME}", parameters: [string(name: 'dummy', value: '')]
    def activeParamDef = paramDef.getProperty(hudson.model.ParametersDefinitionProperty.class)
        .getParameterDefinition('PRODUCTS_LIST')

    activeParamDef.setChoices(options.collect { choice(it, it) })

    paramDef.save()
}
