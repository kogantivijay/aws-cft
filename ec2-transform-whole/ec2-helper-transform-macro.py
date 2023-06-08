import boto3
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ssm = boto3.client('ssm')
parameter = ssm.get_parameter(Name='/app/dsdevops/common/kms/cmk-ebs-key', WithDecryption=True)
KMS_KEY_ARN = parameter['Parameter']['Value']

DEFAULT_IOPS = 3000  # Assign your default IOPS
DEFAULT_SIZE_ROOT = 120  # Assign your default size for root volume
DEFAULT_SIZE_NON_ROOT = 40  # Assign your default size for non-root volume
DEFAULT_THROUGHPUT = 125  # Assign your default throughput
DEFAULT_VOLUME_TYPE = "gp3"  # Assign your default volume type

def handler(event, context):
    try:
        logger.info('Start processing event')
        logger.info(f"Received event: {json.dumps(event, indent=2)}")

        fragment = event['fragment']
        volumes_data = json.loads(event['templateParameterValues']['VolumesJson'])
        logger.info(f"Parsed VolumesJson: {json.dumps(volumes_data, indent=2)}")

        ds_dev_tools_application = event['templateParameterValues']['DSDevToolsApplication']
        logger.info(f"DSDevToolsApplication: {ds_dev_tools_application}")

        ec2_instance_id = {"Ref": "EC2Instance"}
        ec2_instance_az = {"Fn::GetAtt": ["EC2Instance", "AvailabilityZone"]}

        logger.info('Parsed templateParameterValues')

        resources = fragment['Resources']
        logger.info(f"Resources before processing: {resources}")

        block_device_mappings = resources["EC2Instance"]["Properties"].get("BlockDeviceMappings", [])
        logger.info(f"Initial BlockDeviceMappings: {json.dumps(block_device_mappings, indent=2)}")

        for idx, volume in enumerate(volumes_data):
            logger.info(f"Processing volume {idx}: {volume}")
            is_root_volume = volume.get("RootVolume", False)
            ebs_data = {
                "VolumeType": volume.get("VolumeType", DEFAULT_VOLUME_TYPE),
                "Iops": volume.get("Iops", DEFAULT_IOPS),
                "KmsKeyId": KMS_KEY_ARN,
                "Encrypted": True
            }

            logger.info(f"Processing volume {idx}: {json.dumps(ebs_data, indent=2)}")

            if "SnapshotId" in volume:
                ebs_data["SnapshotId"] = volume.get("SnapshotId")
            else:
                if is_root_volume:
                    ebs_data["VolumeSize"] = volume.get("Size", DEFAULT_SIZE_ROOT)
                else:
                    ebs_data["Size"] = volume.get("Size", DEFAULT_SIZE_NON_ROOT)

            if is_root_volume:
                if block_device_mappings:
                    block_device_mappings[0]["Ebs"].update(
                        {k: v for k, v in ebs_data.items() if v is not None}
                    )
                logger.info(f"Updated BlockDeviceMappings for root volume: {block_device_mappings}")
            else:
                ebs_data["Throughput"] = volume.get("Throughput", DEFAULT_THROUGHPUT) if volume.get("VolumeType", "") == "gp3" else None
                ebs_data["Tags"] = volume.get("Tags", [])  # handle the tags
                # Add DSDevToolsApplication as a tag for non-root volumes
                ebs_data["Tags"].append({"Key": "DSDevToolsApplication", "Value": ds_dev_tools_application})

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

        logger.info(f"Final resources: {json.dumps(resources, indent=2)}")
        fragment['Resources'] = resources
        logger.info(f"Final fragment: {json.dumps(fragment, indent=2)}")

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
    logger.info(f"Final Fragment after processing: {json.dumps(response['fragment'], indent=2)}")

    return response
