import groovy.json.JsonSlurper
import groovy.json.JsonBuilder
import groovy.json.JsonOutput

def readJSON(Map args) {
    def file = new File(args.file)
    println "Trying to read file at: ${file.absolutePath}"
    new JsonSlurper().parse(file)
}

def paramsJsonPath = 'sg-transform//params.json'
def maxCharsForSGInputJson = 4050
def maxSplitCountForSGInputJson = 10
def maxCharsForOtherKeys = 4095

def paramsJson = readJSON(file: paramsJsonPath)
println paramsJson

def parameters = []

paramsJson.each { param ->
    def key = param.ParameterKey
    def value = param.ParameterValue

    if (value.startsWith('external-json:')) {
        def externalJsonPath = value.replace('external-json:', '')
        def externalJsonContent = new File('sg-transform//' + externalJsonPath).text.trim()
        def externalJson = new JsonSlurper().parseText(externalJsonContent)
        
        // Retrieve the value from the external JSON using the ParameterKey
        def jsonValue = externalJson[key]
        println "External JSON value: ${jsonValue}"
        
        if (jsonValue == null || jsonValue.contains(null)) {
            error("No corresponding property for ${key} found in the external JSON file.")
        }
        
        // Stringify and split the value into multiple parameters if it exceeds the maximum character limit
        def jsonStr = JsonOutput.toJson(jsonValue)
        println "Total length: ${jsonStr.length()}"
        println "Total lines: ${jsonStr.count('\n')}"
        println "stringified JSON: ${jsonStr}" 

        def maxChars = (key == 'SecurityGroupInputJson') ? maxCharsForSGInputJson : maxCharsForOtherKeys
        def maxSplitCount = (key == 'SecurityGroupInputJson') ? maxSplitCountForSGInputJson : 1

        if (jsonStr.length() > maxChars * maxSplitCount) {
            error("Total character limit exceeded for ${key}. Please reduce the size of the external JSON file.")
        }

        if (jsonStr.length() > maxChars || key == 'SecurityGroupInputJson') {
            def currentPart = ''
            def currentIndex = 1
                
            jsonStr.each { 
                currentPart += it
                if (currentPart.length() > maxChars) {
                    parameters << [
                        ParameterKey: "${key}${currentIndex}",
                        ParameterValue: currentPart
                    ]
                    currentPart = ''
                    currentIndex++
                }
            }
                
            if (currentPart) {
                parameters << [
                    ParameterKey: "${key}${currentIndex}",
                    ParameterValue: currentPart
                ]
            }
        } else {
            parameters << [
                ParameterKey: key,
                ParameterValue: jsonStr
            ]
        }
    } else {
        parameters << [
            ParameterKey: key,
            ParameterValue: value
        ]
    }
}

new File('sg-transform//modified-params.json').write(new JsonBuilder(parameters).toPrettyString())
