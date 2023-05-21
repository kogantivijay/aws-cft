
def call(String propertyName) {
    def jenkinsInstance = Jenkins.getInstanceOrNull()
    def item = jenkinsInstance.getItemByFullName(env.JOB_NAME)

    while(item != null && !(item instanceof com.cloudbees.hudson.plugins.folder.Folder)) {
        item = item.getParent()
    }

    if(item != null) {
        def folderProperties = item.getProperties().getAll(com.cloudbees.hudson.plugins.folder.properties.FolderProperties.class)
        for (property in folderProperties) {
            if (property.getPropertyName().equals(propertyName)) {
                return property.getPropertyValue()
            }
        }
    }

    return null
}

environment {
    TARGET_PRODUCTS = productProperties(PRODUCT_CATEGORY) // Fetch the product properties and set it as an env variable
}

parameters {
    [$class: 'CascadeChoiceParameter', 
        choiceType: 'PT_CHECKBOX', 
        name: 'TARGET_PRODUCTS', 
        description: 'Select the products to deploy',
        script: [$class: 'GroovyScript', 
            fallbackScript: [classpath: [], sandbox: true, script: 
                'return ["Could not get choices"]'],
            script: [classpath: [], sandbox: true, script: 
                '''
                return '${env.TARGET_PRODUCTS}'.split(',') // return the list of products
                '''
            ]
        ]
    ]
}