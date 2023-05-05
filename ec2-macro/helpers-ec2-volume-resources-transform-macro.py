import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    logger.info(f"Received event: {event}")

    fragment = event["fragment"]
    volumes_json = event["params"]["VolumesJson"]
    volumes = json.loads(volumes_json)
    fragment["Resources"] = {}  # Add this line to initialize the Resources
    

    for index, volume in enumerate(volumes):
        volume_resource = f"Volume{index}"
        attachment_resource = f"VolumeAttachment{index}"

        fragment["Resources"][volume_resource] = {
            "Type": "AWS::EC2::Volume",
            "Properties": {
                "AvailabilityZone": {"Fn::GetAtt": ["Instance", "AvailabilityZone"]},
                "Size": volume["Size"],
                "VolumeType": volume["VolumeType"],
                "Iops": volume["Iops"],
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

    response = {
        "Status": "SUCCESS",
        "Fragment": fragment,
    }

    logger.info(f"Response: {response}")

    return response
