# aws-cft
AWS Cloud Formation Templates

# JSON String
 # EbsVolumes:
#  Type: String
#   Default: '[{"DeviceName":"/dev/xvdf","VolumeSize":8,"VolumeType":"gp2"},{"DeviceName":"/dev/xvdg","VolumeSize":16,"VolumeType":"gp2"}]'

# Lambda Test Data

{
  "StackId": "arn:aws:cloudformation:eu-west-1:506271455763:stack/test-stack/fake-id",
  "ResourceProperties": {
    "EbsVolumes": "[{\"DeviceName\":\"/dev/xvdf\",\"VolumeSize\":8,\"VolumeType\":\"gp2\"},{\"DeviceName\":\"/dev/xvdg\",\"VolumeSize\":16,\"VolumeType\":\"gp2\"},{\"DeviceName\":\"/dev/xvdh\",\"VolumeSize\":32,\"VolumeType\":\"gp2\"}]"
  },
  "RequestType": "Create",
  "RequestId": "unique id for this create request",
  "LogicalResourceId": "CustomResourceFunction"
}

{
  "StackId": "arn:aws:cloudformation:eu-west-1:506271455763:stack/test-stack/fake-id",
  "ResourceProperties": {
    "EbsVolumes": [
      {
        "DeviceName": "/dev/xvdf",
        "VolumeSize": 8,
        "VolumeType": "gp2"
      },
      {
        "DeviceName": "/dev/xvdg",
        "VolumeSize": 16,
        "VolumeType": "gp3"
      }
    ]
  },
  "RequestId": "unique id for this create request",
  "LogicalResourceId": "CustomResourceFunction"
}

# Passing via CLI 
aws cloudformation create-stack --stack-name MyStack --template-body file://my_template.yaml --parameters ParameterKey=Tags,ParameterValue='[{"Key":"Environment","Value":"Dev"},{"Key":"Project","Value":"MyProject"}]' ParameterKey=EBSVolumes,ParameterValue='[{"DeviceName":"/dev/xvdf","VolumeSize":8,"VolumeType":"gp2"},{"DeviceName":"/dev/xvdg","VolumeSize":16,"VolumeType":"gp2"}]'

# Custom Resources Vs Macros
Custom Resources:

Pros:
Provides a lot of flexibility in terms of what you can do in the Lambda function.
Allows you to use AWS SDKs or other third-party libraries in your function.
You can use the outputs of the Custom Resource in your CloudFormation stack.
Cons:
Can be slower to create/update/delete resources due to the additional round trip to the Lambda function.
Can be more complex to set up and maintain.
Macros:

Pros:
Can be faster to create/update/delete resources as the changes are made directly to the template.
Simpler to set up and maintain than Custom Resources.
Cons:
Limited to transforming the template at the macro level, i.e. modifying the template itself and not creating/updating/deleting resources.
Limited to 1MB input/output data size.
Cannot use AWS SDKs or third-party libraries in the macro code.

# Bootstrap Pipeline
├── ProductA
│   ├── Dev
│   │   └── *config.yaml  
│   ├── UAT
│   │   └── *config.yaml  
│   └── Prod
│       └── *config.yaml  
├── ProductB
│   |--─ Dev
│   │   └── *config.yaml  
│   |── UAT
│   │   └── *config.yaml  
|   |			
│   └── Prod
│       └── *config.yaml  
|			
└── ...
