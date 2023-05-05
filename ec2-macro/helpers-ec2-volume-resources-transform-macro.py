import json

def handler(event, context):
    fragment = event["Fragment"]
    volumes_json = event["TransformParameterValues"]["VolumesJson"]
    volumes = json.loads(volumes_json)

    for index, volume in enumerate(volumes):
        volume_resource = f"Volume{index}"
        attachment_resource = f"VolumeAttachment{index}"

        fragment["Resources"][volume_resource] = {
            "Type": "AWS::EC2::Volume",
            "Properties": {
                "AvailabilityZone": {"Fn::Select": [0, {"Fn::GetAZs": ""}]},
                "Size": volume["Size"],
                "VolumeType": volume["VolumeType"],
                "Iops": volume["Iops"],
                "KmsKeyId": volume["KmsKeyId"],
            },
        }

        fragment["Resources"][attachment_resource] = {
            "Type": "AWS::EC2::VolumeAttachment",
            "Properties": {
                "InstanceId": {"Ref": "Instance"},
                "VolumeId": {"Ref": volume_resource},
                "Device": volume["Device"],
            },
        }

    return {
        "Status": "SUCCESS",
        "Fragment": fragment,
    }
