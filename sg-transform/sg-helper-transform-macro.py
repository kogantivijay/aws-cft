import json
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ssm = boto3.client('ssm')


def transform_security_group_template(input_json, application):
    transformed_template = []

    for group in input_json:
        name = group['name']
        description = group.get('description', '')
        rules = group['rules']
        tags = group.get('tags', [])

        transformed_rules = []
        for rule in rules:
            rule_type = rule['type']
            from_port = rule.get('fromPort')
            to_port = rule.get('toPort')
            description = rule.get('description', '')
            cidr_ranges = rule.get('cidrRanges', [])
            source_security_group_id = resolve_ssm_parameter(rule.get('sourceSecurityGroupId', ''))
            destination_security_group_id = resolve_ssm_parameter(rule.get('destinationSecurityGroupId', ''))

            # Validate fromPort and toPort
            if rule_type == 'ingress' and (from_port is None or to_port is None):
                raise ValueError("Missing 'fromPort' or 'toPort' in ingress rule.")
            elif rule_type == 'egress' and (from_port is None or to_port is None):
                raise ValueError("Missing 'fromPort' or 'toPort' in egress rule.")

            if rule.get('ipProtocol') == '-1':
                raise ValueError("Invalid value '-1' specified for 'ipProtocol' in rule.")

            transformed_rule = {
                'FromPort': from_port,
                'ToPort': to_port,
                'Description': description,
                'IpProtocol': rule.get('ipProtocol', 'tcp')
            }

            if rule_type == 'ingress':
                if destination_security_group_id:
                    raise ValueError("Ingress rule should not have 'destinationSecurityGroupId'.")
                if source_security_group_id:
                    transformed_rule['SourceSecurityGroupId'] = source_security_group_id
                elif cidr_ranges:
                    transformed_rule['CidrIp'] = cidr_ranges[0]
            elif rule_type == 'egress':
                if source_security_group_id:
                    raise ValueError("Egress rule should not have 'sourceSecurityGroupId'.")
                if destination_security_group_id:
                    transformed_rule['DestinationSecurityGroupId'] = destination_security_group_id
                elif cidr_ranges:
                    transformed_rule['CidrIp'] = cidr_ranges[0]

            transformed_rules.append(transformed_rule)

        transformed_group = {
            'Type': 'AWS::EC2::SecurityGroup',
            'Properties': {
                'GroupName': name,
                'GroupDescription': description,
                'VpcId': resolve_ssm_parameter(f'/app/common/security-groups/{application}-VpcId'),
                'SecurityGroupIngress': [],
                'SecurityGroupEgress': [],
                'Tags': [{'Key': 'iamfilter', 'Value': application}] + tags
            }
        }

        for rule in transformed_rules:
            rule_type = 'SecurityGroupIngress' if rule_type == 'ingress' else 'SecurityGroupEgress'
            transformed_group['Properties'][rule_type].append(rule)

        transformed_template.append(transformed_group)

    return transformed_template


def create_ssm_parameter_blocks(transformed_template, application):
    ssm_parameters = []
    for group in transformed_template:
        ssm_parameter = {
            'Type': 'AWS::SSM::Parameter',
            'Properties': {
                'Name': f"/app/common/security-groups/{application}-{group['Properties']['GroupName']}",
                'Description': "SSM Parameter for Security Group ID",
                'Type': 'String',
                'Value': {'Fn::GetAtt': [group['Properties']['GroupName'], 'GroupId']}
            }
        }
        ssm_parameters.append(ssm_parameter)

    return ssm_parameters


def resolve_ssm_parameter(parameter):
    if parameter.startswith('ssm:'):
        ssm_parameter_name = parameter[4:]
        try:
            response = ssm.get_parameter(Name=ssm_parameter_name, WithDecryption=True)
            parameter_value = response['Parameter']['Value']
            return parameter_value
        except Exception as e:
            logger.error(f"Error resolving SSM parameter '{ssm_parameter_name}': {e}")
            raise ValueError(f"Failed to resolve SSM parameter '{ssm_parameter_name}'")
    else:
        return parameter


def lambda_handler(event, context):
    try:
        logger.info('Transform Security Group Template')
        input_json = event['input']
        application = event['application']
        logger.info(f"Input JSON: {json.dumps(input_json, indent=2)}")

        transformed_template = transform_security_group_template(input_json, application)
        logger.info(f"Transformed Template: {json.dumps(transformed_template, indent=2)}")

        ssm_parameters = create_ssm_parameter_blocks(transformed_template, application)
        logger.info(f"SSM Parameters: {json.dumps(ssm_parameters, indent=2)}")

        fragment = {
            'requestId': event['requestId'],
            'status': 'success',
            'fragment': transformed_template + ssm_parameters
        }
        return fragment

    except ValueError as e:
        logger.error(f"Error: {str(e)}")
        fragment = {
            'requestId': event['requestId'],
            'status': 'failure',
            'fragment': {},
            'errorMessage': str(e),
            'errorType': type(e).__name__
        }
        return fragment

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        fragment = {
            'requestId': event['requestId'],
            'status': 'failure',
            'fragment': {},
            'errorMessage': "An unexpected error occurred.",
            'errorType': type(e).__name__
        }
        return fragment
