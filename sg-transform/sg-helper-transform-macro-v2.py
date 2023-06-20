def transform_security_group_template(input_json, application):
    transformed_template = {
        'AWSTemplateFormatVersion': '2010-09-09',
        'Resources': {},
        'Outputs': {}
    }

    for i, group in enumerate(input_json, start=1):
        name = group['name']
        description = group.get('description', '')
        rules = group['rules']
        tags = group.get('tags', [])

        security_group_resource_name = f'SecurityGroup{i}'
        ingress_resource_name = f'SecurityGroup{i}Ingress'
        egress_resource_name = f'SecurityGroup{i}Egress'

        # Create Security Group resource
        security_group_resource = {
            'Type': 'AWS::EC2::SecurityGroup',
            'Properties': {
                'GroupName': name,
                'GroupDescription': description,
                'VpcId': resolve_ssm_parameter(f'/app/common/security-groups/{application}-VpcId'),
                'Tags': [{'Key': 'iamfilter', 'Value': application}] + tags
            }
        }
        transformed_template['Resources'][security_group_resource_name] = security_group_resource

        ingress_rules = []
        egress_rules = []

        # Process rules
        for j, rule in enumerate(rules, start=1):
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

            rule_resource_name = f'{security_group_resource_name}Rule{j}'

            if rule_type == 'ingress':
                if destination_security_group_id:
                    raise ValueError("Ingress rule should not have 'destinationSecurityGroupId'.")
                if source_security_group_id:
                    ingress_rule = {
                        'Type': 'AWS::EC2::SecurityGroupIngress',
                        'Properties': {
                            'GroupName': {'Ref': security_group_resource_name},
                            'IpProtocol': rule.get('ipProtocol', 'tcp'),
                            'FromPort': from_port,
                            'ToPort': to_port,
                            'Description': description,
                            'SourceSecurityGroupId': source_security_group_id
                        }
                    }
                    transformed_template['Resources'][rule_resource_name] = ingress_rule
            elif rule_type == 'egress':
                if source_security_group_id:
                    raise ValueError("Egress rule should not have 'sourceSecurityGroupId'.")
                if destination_security_group_id:
                    egress_rule = {
                        'Type': 'AWS::EC2::SecurityGroupEgress',
                        'Properties': {
                            'GroupName': {'Ref': security_group_resource_name},
                            'IpProtocol': rule.get('ipProtocol', 'tcp'),
                            'FromPort': from_port,
                            'ToPort': to_port,
                            'Description': description,
                            'DestinationSecurityGroupId': destination_security_group_id
                        }
                    }
                    transformed_template['Resources'][rule_resource_name] = egress_rule

            for k, cidr_range in enumerate(cidr_ranges, start=1):
                if rule_type == 'ingress':
                    ingress_rule = {
                        'Type': 'AWS::EC2::SecurityGroupIngress',
                        'Properties': {
                            'GroupName': {'Ref': security_group_resource_name},
                            'IpProtocol': rule.get('ipProtocol', 'tcp'),
                            'FromPort': from_port,
                            'ToPort': to_port,
                            'Description': description,
                            f'CidrIp{k}': cidr_range
                        }
                    }
                    transformed_template['Resources'][f'{rule_resource_name}Cidr{k}'] = ingress_rule
                elif rule_type == 'egress':
                    egress_rule = {
                        'Type': 'AWS::EC2::SecurityGroupEgress',
                        'Properties': {
                            'GroupName': {'Ref': security_group_resource_name},
                            'IpProtocol': rule.get('ipProtocol', 'tcp'),
                            'FromPort': from_port,
                            'ToPort': to_port,
                            'Description': description,
                            f'CidrIp{k}': cidr_range
                        }
                    }
                    transformed_template['Resources'][f'{rule_resource_name}Cidr{k}'] = egress_rule

    return transformed_template
