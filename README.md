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

Ec2 Instance Types
    AllowedValues: [
      'c5n.large', 'c5n.xlarge', 'c5n.2xlarge', 'c5n.4xlarge', 'c5n.9xlarge', 'c5n.18xlarge', 
      'c6i.large', 'c6i.xlarge', 'c6i.2xlarge', 'c6i.4xlarge', 'c6i.8xlarge', 'c6i.12xlarge', 'c6i.16xlarge', 'c6i.24xlarge', 'c6i.32xlarge', 
      'c6a.large', 'c6a.xlarge', 'c6a.2xlarge', 'c6a.4xlarge', 'c6a.8xlarge', 'c6a.12xlarge', 'c6a.16xlarge', 'c6a.24xlarge', 
      'r5n.large', 'r5n.xlarge', 'r5n.2xlarge', 'r5n.4xlarge', 'r5n.8xlarge', 'r5n.12xlarge', 'r5n.16xlarge', 'r5n.24xlarge', 
      'r6a.large', 'r6a.xlarge', 'r6a.2xlarge', 'r6a.4xlarge', 'r6a.8xlarge', 'r6a.12xlarge', 'r6a.16xlarge', 'r6a.24xlarge', 
      'r6i.large', 'r6i.xlarge', 'r6i.2xlarge', 'r6i.4xlarge', 'r6i.8xlarge', 'r6i.12xlarge', 'r6i.16xlarge', 'r6i.24xlarge', 
      'm6a.large', 'm6a.xlarge', 'm6a.2xlarge', 'm6a.4xlarge', 'm6a.8xlarge', 'm6a.12xlarge', 'm6a.16xlarge', 'm6a.24xlarge', 
      'm6i.large', 'm6i.xlarge', 'm6i.2xlarge', 'm6i.4xlarge', 'm6i.8xlarge', 'm6i.12xlarge', 'm6i.16xlarge', 'm6i.24xlarge', 
      'm6n.large', 'm6n.xlarge', 'm6n.2xlarge', 'm6n.4xlarge', 'm6n.8xlarge', 'm6n.12xlarge', 'm6n.16xlarge', 'm6n.24xlarge'
    ]


    How to test the lambda
   {
  "fragment": {
    "Resources": {
      "EC2Instance": {
        "Properties": {
          "BlockDeviceMappings": []
        }
      }
    }
  },
  "templateParameterValues": {
    "VolumesJson": "[{\"RootVolume\": true, \"VolumeType\": \"gp2\", \"Size\": 50, \"Device\": \"/dev/xvda\"}], { \"VolumeType\": \"gp2\", \"Size\": 50, \"Device\": \"/dev/xvdf\"}",
    "DSDevToolsApplication": "TestApp"
  },
  "requestId": "123456"
}


{
  "requestId": "unique-request-id",
  "fragment": {
    "Resources": {
      "EC2Instance": {
        "Properties": {}
      }
    }
  },
  "templateParameterValues": {
    "VolumesJson": "[{\"VolumeType\":\"gp2\",\"Size\":50,\"Device\":\"/dev/sda1\",\"RootVolume\":true}]",
    "InstanceTagsJson": "{\"Name\":\"TestInstance\",\"Environment\":\"Dev\"}",
    "SecurityGroupIDSSMJson": "[\"/app/team/security-groups/sg1\",\"/app/team/security-groups/sg2\"]",
    "DevToolsApplication": "testApp",
     "UserDataJson": "{\"Application\": {\"SERVER\": {\"NAS_IP\": \"28.X\"}}, \"cHEF_RunList\": \"role[dxdt],role[ds]\", \"ca_env\": \"dev\"}"
  }
}

