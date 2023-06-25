 import groovy.json.JsonSlurper
import groovy.json.JsonBuilder
import groovy.json.JsonOutput

def readJSON(Map args) {
    def file = new File(args.file)
    println "Trying to read file at: ${file.absolutePath}"
    new JsonSlurper().parse(file)
}

def paramsJsonPath = 'sg-transform\\params.json'
def maxChars = 2000
def maxSplitCount = 10

def paramsJson = readJSON(file: paramsJsonPath) //In jenkins Pipeline no need of seperate definition
println paramsJson

def parameters = []

paramsJson.each { param ->
    def key = param.Key
    def value = param.Value
    
    if (value.startsWith('external:json:')) {
        def externalJsonPath = value.replace('external:json:', '')
        //def externalJsonContent = readFile('sg-transform\\' + externalJsonPath).trim() // In jenkins Pipeline
        def externalJsonContent = new File('sg-transform\\' + externalJsonPath).text.trim()
        //println "External JSON content: ${externalJsonContent}" 
        //def externalJsonValue = new groovy.json.JsonBuilder(externalJsonContent).toPrettyString()
        def json = new JsonSlurper().parseText(externalJsonContent)

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
                //println "Current part length: ${currentPart.length()}" 
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

//writeFile(file: 'sg-transform//modified-params.json', text: new groovy.json.JsonBuilder(parameters).toPrettyString())
new File('sg-transform/modified-params.json').write(new JsonBuilder(parameters).toPrettyString())