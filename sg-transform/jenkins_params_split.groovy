pipeline {
    agent any

    stages {
        stage('Modify JSON') {
            steps {
                script {
                    def paramsJsonPath = 'sg-transform\\params.json'
                    def maxChars = 2000
                    def maxSplitCount = 10

                    def paramsJson = readJson file: paramsJsonPath
                    println paramsJson

                    def parameters = []

                    paramsJson.each { param ->
                        def key = param.Key
                        def value = param.Value

                        if (value.startsWith('external:json:')) {
                            def externalJsonPath = value.replace('external:json:', '')
                            def externalJsonContent = readFile('sg-transform\\' + externalJsonPath).trim()
                            def json = readJSON(text: externalJsonContent)

                            def jsonStr = JsonOutput.toJson(json)
                            println "Total length: ${jsonStr.length()}"
                            println "Total lines: ${jsonStr.count('\n')}"
                            println "stringified JSON: ${jsonStr}" 

                            if (jsonStr.length() > maxChars * maxSplitCount) {
                                error("Total character limit exceeded. Please reduce the size of the external JSON file.")
                            }

                            // Split the value into multiple parameters if it exceeds the maximum character limit
                            if (jsonStr.length() >= maxChars) {
                                def currentPart = ''
                                def currentIndex = 1

                                jsonStr.each { 
                                    currentPart += it
                                    println "Current part length: ${currentPart.length()}" 
                                    if (currentPart.length() > maxChars) {
                                        parameters << [
                                            Key: "securityGroupJson${currentIndex}",
                                            Value: currentPart
                                        ]
                                        currentPart = ''
                                        currentIndex++
                                    }
                                }

                                if (currentPart) {
                                    parameters << [
                                        Key: "securityGroupJson${currentIndex}",
                                        Value: currentPart
                                    ]
                                }
                            } else {
                                parameters << [
                                    Key: key,
                                    Value: jsonStr
                                ]
                            }
                        } else {
                            parameters << [
                                Key: key,
                                Value: value
                            ]
                        }
                    }

                    writeFile(file: 'sg-transform//modified-params.json', text: new groovy.json.JsonBuilder(parameters).toPrettyString())
                }
            }
        }
    }
}
