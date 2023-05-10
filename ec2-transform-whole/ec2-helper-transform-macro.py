import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    try:
        logger.info(f"Event: {event}")

        fragment = event['fragment']
        volumes_data = json.loads(event['templateParameterValues']['VolumesJson'])
        ec2_instance_id = {"Ref": "Instance"}
        ec2_instance_az = {"Fn::GetAtt": ["Instance", "AvailabilityZone"]}

        resources = fragment['Resources']

        block_device_mappings = []

        for idx, volume in enumerate(volumes_data, start=1):
            volume_resource_name = f"Volume{idx}"
            attachment_resource_name = f"VolumeAttachment{idx}"

            resources[volume_resource_name] = {
                "Type": "AWS::EC2::Volume",
                "Properties": {
                    "Size": volume["Size"],
                    "AvailabilityZone": ec2_instance_az,
                    "VolumeType": volume["VolumeType"],
                    "Iops": volume["Iops"],
                }
            }

            if volume.get("RootVolume", False):
                block_device_mappings.append({
                    "DeviceName": volume["Device"],
                    "Ebs": {
                        "VolumeSize": volume["Size"],
                        "VolumeType": volume["VolumeType"],
                        "Iops": volume["Iops"],
                    }
                })
            else:
                resources[attachment_resource_name] = {
                    "Type": "AWS::EC2::VolumeAttachment",
                    "Properties": {
                        "Device": volume["Device"],
                        "InstanceId": ec2_instance_id,
                        "VolumeId": {"Ref": volume_resource_name}
                    }
                }
                logger.info(f"Added volume {volume_resource_name} and attachment {attachment_resource_name}")

        if block_device_mappings:
            resources["Instance"]["Properties"]["BlockDeviceMappings"] = block_device_mappings

        response = {
            'requestId': event['requestId'],
            'status': 'success',
            'fragment': fragment
        }

    except Exception as e:
        logger.error(f"Error processing event: {e}")
        response = {
            'requestId': event['requestId'],
            'status': 'failure',
            'fragment': fragment,
            'errorMessage': str(e),
            'errorType': type(e).__name__
        }

    logger.info(f"Response status: {response['status']}")
    logger.info(f"Fragment after processing: {response['fragment']}")

    return response
