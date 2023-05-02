import json
import random
import os
import requests

def generate_ebs_volume_mappings(ebs_volumes_json):
    ebs_volume_mappings = []

    for volume in ebs_volumes_json:
        device_name = volume['DeviceName']
        volume_size = volume['VolumeSize']
        volume_type = volume['VolumeType']

        ebs_volume_mappings.append({
            'DeviceName': device_name,
            'Ebs': {
                'VolumeSize': volume_size,
                'VolumeType': volume_type
            }
        })

    return ebs_volume_mappings

def lambda_handler(event, context):
    random_number = random.randint(1, 100)
    # ebs_volumes_json = event['ResourceProperties']['EbsVolumes']
    # ebs_volume_mappings = generate_ebs_volume_mappings(ebs_volumes_json)

    response_data = {
        'RandomNumber': random_number
        # 'EBSVolumeMappings': ebs_volume_mappings
    }

    response = {
        'Status': 'SUCCESS',
        'PhysicalResourceId': context.log_stream_name,
        'StackId': event['StackId'],
        'RequestId': event['RequestId'],
        'LogicalResourceId': event['LogicalResourceId'],
        'Data': response_data
    }

    if 'ResponseURL' in event:
        headers = {'Content-Type': ''}
        requests.put(event['ResponseURL'], data=json.dumps(response), headers=headers)

    return response
