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


