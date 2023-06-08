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


def validate_volumes_data(volumes_data):
    for idx, volume in enumerate(volumes_data):
        required_keys = ["VolumeType", "Size", "Device"]

        for key in required_keys:
            if key not in volume:
                raise ValueError(f"Volume {idx} is missing required key '{key}'")
        case_sensitive_keys = ["RootVolume", "VolumeType", "Device"]
        # TODO: Write logic to do case sensitive check for keys 


def add_volumes(resources, volumes_data, ds_dev_tools_application, ec2_instance_id):
    block_device_mappings = resources["EC2Instance"]["Properties"].get("BlockDeviceMappings", [])

    for idx, volume in enumerate(volumes_data):
        logger.info(f"Processing volume {idx}: {volume}")
        is_root_volume = volume.get("RootVolume", False)
        volume_type = volume.get("VolumeType", DEFAULT_VOLUME_TYPE)

        ebs_data = {
            "VolumeType": volume_type,
            "KmsKeyId": KMS_KEY_ARN,
            "Encrypted": True
        }

        if "SnapshotId" in volume:
            ebs_data["SnapshotId"] = volume.get("SnapshotId")
        else:
            if is_root_volume:
                ebs_data["VolumeSize"] = volume.get("Size", DEFAULT_SIZE_ROOT)
            else:
                ebs_data["Size"] = volume.get("Size", DEFAULT_SIZE_NON_ROOT)

        if volume_type in ["gp3", "io1", "io2"]:
            ebs_data["Iops"] = volume.get("Iops", DEFAULT_IOPS)

        logger.info(f"Processed volume {idx}: {json.dumps(ebs_data, indent=2)}")

        if is_root_volume:
            if block_device_mappings:
                block_device_mappings[0]["Ebs"].update(
                    {k: v for k, v in ebs_data.items() if v is not None}
                )
            logger.info(f"Updated BlockDeviceMappings for root volume: {block_device_mappings}")
        else:
            if volume_type == "gp3":
                ebs_data["Throughput"] = volume.get("Throughput", DEFAULT_THROUGHPUT)

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


def add_instance_tags(resources, instance_tags, ds_dev_tools_application):
    default_tags = [{"Key": "DSDevToolsApplication", "Value": ds_dev_tools_application}]
    instance_resource_name = "EC2Instance"
    instance_resource = resources.get(instance_resource_name, {})
    instance_properties = instance_resource.get("Properties", {})
    existing_tags = instance_properties.get("Tags", [])
    updated_tags = existing_tags + default_tags
    for key, value in instance_tags.items():
        updated_tags.append({"Key": key, "Value": value})
    instance_properties["Tags"] = updated_tags
    instance_resource["Properties"] = instance_properties
    resources[instance_resource_name] = instance_resource


def add_security_groups(resources, security_group_ids):
    instance_resource_name = "EC2Instance"
    instance_resource = resources.get(instance_resource_name, {})
    instance_properties = instance_resource.get("Properties", {})
    instance_properties["SecurityGroupIds"] = []

    # Retrieve the default security group ID from SSM
    default_sg_ssm_key = "/app/dsdevops/common/default-security-group-id"  # Replace with the actual SSM parameter key
    response = ssm.get_parameter(Name=default_sg_ssm_key)
    default_sg_id = response['Parameter']['Value']

    # Add the default security group ID only if it's not already present in the list
    if default_sg_id not in security_group_ids:
        instance_properties["SecurityGroupIds"].append(default_sg_id)

    for ssm_key in security_group_ids:
        response = ssm.get_parameter(Name=ssm_key)
        sg_id = response['Parameter']['Value']
        instance_properties["SecurityGroupIds"].append(sg_id)

    instance_resource["Properties"] = instance_properties
    resources[instance_resource_name] = instance_resource


def handler(event, context):
    try:
        logger.info('Start processing event')
        logger.info(f"Received event: {json.dumps(event, indent=2)}")

        fragment = event['fragment']
        volumes_data = json.loads(event['templateParameterValues']['VolumesJson'])
        instance_tags = json.loads(event['templateParameterValues'].get('InstanceTagsJson', ''))
        security_group_ids_json = event['templateParameterValues'].get('SecurityGroupIDSSMJson', '[]')

        logger.info(f"Parsed VolumesJson: {json.dumps(volumes_data, indent=2)}")
        logger.info(f"Parsed InstanceTagsJson: {json.dumps(instance_tags, indent=2)}")
        logger.info(f"Parsed SecurityGroupIDSSMJson: {security_group_ids_json}")

        ds_dev_tools_application = event['templateParameterValues']['DSDevToolsApplication']
        logger.info(f"DSDevToolsApplication: {ds_dev_tools_application}")

        ec2_instance_id = {"Ref": "EC2Instance"}
        ec2_instance_az = {"Fn::GetAtt": ["EC2Instance", "AvailabilityZone"]}

        logger.info('Parsed templateParameterValues')

        resources = fragment['Resources']
        logger.info(f"Resources before processing: {resources}")

        block_device_mappings = resources["EC2Instance"]["Properties"].get("BlockDeviceMappings", [])
        logger.info(f"Initial BlockDeviceMappings: {json.dumps(block_device_mappings, indent=2)}")

        validate_volumes_data(volumes_data)
        logger.info('validate_volumes_data() completed')
        
        add_volumes(resources, volumes_data, ds_dev_tools_application, ec2_instance_id)
        logger.info('add_volumes() completed')
                
        add_instance_tags(resources, instance_tags, ds_dev_tools_application)
        logger.info('add_instance_tags() completed')

        security_group_ids = json.loads(security_group_ids_json)
        add_security_group_ids(resources, security_group_ids)
        logger.info('add_security_group_ids() completed')

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
