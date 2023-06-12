import json
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ssm = boto3.client('ssm')


def transform_security_group_template(input_json):
    transformed_template = []

    for group in input_json:
        name = group['name']
        description = group.get('description', '')
        rules = group['rules']
        transformed_rules = []

        for rule in rules:
            rule_type = rule['type']
            from_port = rule.get('fromPort')
            to_port = rule.get('toPort')
            description = rule.get('description', '')
            cidr_ranges = rule.get('cidrRanges', [])
            source_security_group_id = resolve_ssm_parameter(rule.get('sourceSecurityGroupId', ''))
            destination_security_group_id = resolve_ssm_parameter(rule.get('destinationSecurityGroupId', ''))

            if rule_type == 'ingress':
                if from_port is None or to_port is None:
                    raise ValueError("Missing 'fromPort' or 'toPort' in ingress rule.")

                ingress_rule = {}
                ingress_rule['FromPort'] = from_port
                ingress_rule['ToPort'] = to_port
                ingress_rule['Description'] = description

                if source_security_group_id:
                    ingress_rule['SourceSecurityGroupId'] = source_security_group_id
                elif cidr_ranges:
                    ingress_rule['CidrIp'] = cidr_ranges[0]

                if rule.get('ipProtocol') == '-1':
                    raise ValueError("Invalid value '-1' specified for 'ipProtocol' in ingress rule.")

                # Set default value for IpProtocol
                ingress_rule['IpProtocol'] = rule.get('ipProtocol', 'tcp')

                transformed_rules.append(ingress_rule)

            elif rule_type == 'egress':
                if from_port is None or to_port is None:
                    raise ValueError("Missing 'fromPort' or 'toPort' in egress rule.")

                egress_rule = {}
                egress_rule['FromPort'] = from_port
                egress_rule['ToPort'] = to_port
                egress_rule['Description'] = description

                if destination_security_group_id:
                    egress_rule['DestinationSecurityGroupId'] = destination_security_group_id
                elif cidr_ranges:
                    egress_rule['CidrIp'] = cidr_ranges[0]

                if rule.get('ipProtocol') == '-1':
                    raise ValueError("Invalid value '-1' specified for 'ipProtocol' in egress rule.")

                # Set default value for IpProtocol
                egress_rule['IpProtocol'] = rule.get('ipProtocol', 'tcp')

                transformed_rules.append(egress_rule)

        transformed_group = {
            'name': name,
            'description': description,
            'rules': transformed_rules
        }

        transformed_template.append(transformed_group)

    return transformed_template


def resolve_ssm_parameter(parameter):
    # Placeholder logic to resolve SSM parameter
    # Replace with your actual SSM parameter resolution logic
    # For example, you can use Boto3 to fetch the parameter value
    if parameter.startswith('ssm:'):
        ssm_parameter_name = parameter[4:]
        try:
            # Fetch the SSM parameter value using Boto3
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
        logger.info(f"Input JSON: {json.dumps(input_json, indent=2)}")

        transformed_template = transform_security_group_template(input_json)
        logger.info(f"Transformed Template: {json.dumps(transformed_template, indent=2)}")

        return {
            'statusCode': 200,
            'body': json.dumps(transformed_template)
        }
    except ValueError as e:
        logger.error(f"Error: {str(e)}")
        return {
            'statusCode': 400,
            'body': str(e)
        }
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            'statusCode': 500,
            'body': "An unexpected error occurred."
        }
