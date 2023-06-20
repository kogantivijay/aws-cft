import boto3
import json

# Create EC2 resource object
ec2 = boto3.resource('ec2')

# List of your Security Group IDs
sg_ids = ["sg-0123456789abcdef0", "sg-0123456789abcdef1", "sg-0123456789abcdef2"]

security_groups = []

for sg_id in sg_ids:
    # Fetch security group details
    group = ec2.SecurityGroup(sg_id)

    security_group = {}
    security_group["groupName"] = group.group_name
    security_group["groupDescription"] = group.description
    security_group["groupLogicalID"] = f"SecurityGroup{sg_ids.index(sg_id)+1}"
    security_group["rules"] = []

    # Fetch ingress rules
    for i, ingress_rule in enumerate(group.ip_permissions, start=1):
        rule = {}
        rule["type"] = "ingress"
        rule["ruleLogicalID"] = f"{security_group['groupLogicalID']}Rule{i}"
        rule["fromPort"] = ingress_rule.get('FromPort', '')
        rule["toPort"] = ingress_rule.get('ToPort', '')
        rule["cidrRanges"] = [i['CidrIp'] for i in ingress_rule['IpRanges']]
        rule["description"] = ingress_rule['IpRanges'][0].get('Description', '') if ingress_rule['IpRanges'] else ''
        if ingress_rule.get('UserIdGroupPairs'):
            rule["sourceSecurityGroupId"] = ingress_rule['UserIdGroupPairs'][0]['GroupId']
        security_group["rules"].append(rule)

    # Fetch egress rules
    for i, egress_rule in enumerate(group.ip_permissions_egress, start=1):
        rule = {}
        rule["type"] = "egress"
        rule["ruleLogicalID"] = f"{security_group['groupLogicalID']}Rule{i}"
        rule["fromPort"] = egress_rule.get('FromPort', '')
        rule["toPort"] = egress_rule.get('ToPort', '')
        rule["cidrRanges"] = [i['CidrIp'] for i in egress_rule['IpRanges']]
        rule["description"] = egress_rule['IpRanges'][0].get('Description', '') if egress_rule['IpRanges'] else ''
        if egress_rule.get('UserIdGroupPairs'):
            rule["destinationSecurityGroupId"] = egress_rule['UserIdGroupPairs'][0]['GroupId']
        security_group["rules"].append(rule)

    security_groups.append(security_group)

print(json.dumps(security_groups, indent=2))
