import boto3
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ssm = boto3.client('ssm')
parameter = ssm.get_parameter(Name='/app/dsdevops/common/kms/cmk-ebs-key', WithDecryption=True)
KMS_KEY_ARN = parameter['Parameter']['Value']

def handler(event, context):
    try:
        logger.info(f"Event: {event}")

        fragment = event['fragment']
        volumes_data = json.loads(event['templateParameterValues']['VolumesJson'])
        ec2_instance_id = {"Ref": "EC2Instance"}
        ec2_instance_az = {"Fn::GetAtt": ["EC2Instance", "AvailabilityZone"]}

        resources = fragment['Resources']

        block_device_mappings = resources["EC2Instance"]["Properties"].get("BlockDeviceMappings", [])

        for idx, volume in enumerate(volumes_data):
            is_root_volume = volume.get("RootVolume", False)
            ebs_data = {
                "VolumeSize": volume.get("Size", None),
                "VolumeType": volume.get("VolumeType", None),
                "Iops": volume.get("Iops", None),
                "KmsKeyId": KMS_KEY_ARN,
                "Encrypted": True
            }

            if is_root_volume:
                if block_device_mappings:
                    block_device_mappings[0]["Ebs"].update(
                        {k: v for k, v in ebs_data.items() if v is not None}
                    )
            else:
                ebs_data["Throughput"] = volume.get("Throughput", None) if volume.get("VolumeType", "") == "gp3" else None

                volume_resource_name = f"Volume{idx}"
                attachment_resource_name = f"VolumeAttachment{idx}"

                resources[volume_resource_name] = {
                    "Type": "AWS::EC2::Volume",
                    "DeletionPolicy": "Retain",
                    "UpdateReplacePolicy": "Retain",
                    "Properties": ebs_data
                }

                resources[attachment_resource_name] = {
                    "Type": "AWS::EC2::VolumeAttachment",
                    "Properties": {
                        "Device": volume["Device"],
                        "InstanceId": ec2_instance_id,
                        "VolumeId": {"Ref": volume_resource_name}
                    }
                }

                logger.info(f"Added volume {volume_resource_name} and attachment {attachment_resource_name}")

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
