# Security Group Product Template

This CloudFormation template allows you to create security groups with flexible ingress and egress rules. The template utilizes a Transform Macro Lambda function to transform the input JSON into the required CloudFormation format.

## Usage

### Input JSON Format

The input JSON for the security group template should follow the following structure:

```json
[
  {
    "name": "SecurityGroup-1",
    "description": "Description of SecurityGroup-1",
    "rules": [
      {
        "type": "ingress",
        "fromPort": 22,
        "toPort": 23,
        "cidrRanges": ["26.1.12.0/24", "28.0.0.0/8", "27.0.0.1/32"],
        "description": "Description of ingress rule"
      },
      {
        "type": "egress",
        "fromPort": 27,
        "toPort": 29,
        "description": "Description of egress rule",
        "destinationSecurityGroupId": "ssm:/path/to/destinationSecurityGroupId"
      }
    ]
  },
  {
    "name": "SecurityGroup-2",
    "description": "Description of SecurityGroup-2",
    "rules": [
      {
        "type": "ingress",
        "fromPort": 443,
        "toPort": 443,
        "description": "Description of ingress rule",
        "sourceSecurityGroupId": "ssm:/path/to/sourceSecurityGroupId"
      },
      {
        "type": "egress",
        "fromPort": 27,
        "toPort": 29,
        "cidrRanges": ["21.1.12.0/24", "18.0.0.0/8", "17.0.0.1/32"],
        "description": "Description of egress rule"
      }
    ]
  },
  {
    "name": "SecurityGroup-3",
    "description": "Description of SecurityGroup-3",
    "rules": [
      {
        "type": "egress",
        "fromPort": 636,
        "toPort": 636,
        "cidrRanges": ["26.1.12.0/24", "28.0.0.0/8", "27.0.0.1/32"],
        "description": "Description of egress rule"
      },
      {
        "type": "egress",
        "fromPort": 27,
        "toPort": 29,
        "cidrRanges": ["21.1.12.0/24", "18.0.0.0/8", "17.0.0.1/32"],
        "description": "Description of egress rule"
      }
    ]
  }
]
```

### Template Transformation

The input JSON is transformed into the CloudFormation template format using the Transform Macro Lambda function. The macro performs the following transformations:

- Resolves SSM parameter references for `sourceSecurityGroupId` and `destinationSecurityGroupId`.
- Validates the input by checking for missing required fields and invalid values.
- Sets default values for `ipProtocol` if not provided.
- Maps the input JSON to the CloudFormation resource format.

### Output CloudFormation Template

The transformed template will contain the security group resources based on the input JSON. Each security group will have the specified name, description, and rules.

### Examples

Here are some examples of how to use the Security Group Product Template:

#### Example 1: Basic Ingress and Egress

 Rules

```json
[
  {
    "name": "SecurityGroup-1",
    "description": "Security Group 1",
    "rules": [
      {
        "type": "ingress",
        "fromPort": 80,
        "toPort": 80,
        "cidrRanges": ["0.0.0.0/0"],
        "description": "HTTP access"
      },
      {
        "type": "egress",
        "fromPort": 0,
        "toPort": 0,
        "cidrRanges": ["0.0.0.0/0"],
        "description": "All outbound traffic"
      }
    ]
  }
]
```

#### Example 2: Multiple Rules for a Security Group

```json
[
  {
    "name": "SecurityGroup-2",
    "description": "Security Group 2",
    "rules": [
      {
        "type": "ingress",
        "fromPort": 22,
        "toPort": 22,
        "cidrRanges": ["10.0.0.0/16"],
        "description": "SSH access within VPC"
      },
      {
        "type": "ingress",
        "fromPort": 443,
        "toPort": 443,
        "cidrRanges": ["0.0.0.0/0"],
        "description": "HTTPS access from anywhere"
      },
      {
        "type": "egress",
        "fromPort": 0,
        "toPort": 0,
        "cidrRanges": ["0.0.0.0/0"],
        "description": "All outbound traffic"
      }
    ]
  }
]
```

### Security Group Limitations

- The Security Group Product Template has the following limitations:
  - The template does not support complex rule configurations such as ICMP, prefix lists, or source/destination security group name references.
  - The template only supports IPv4 CIDR ranges.
  - The template does not handle overlapping rule ranges or rule conflicts. Please ensure that the rules do not conflict with each other.

---

Please provide this documentation to the consumers of your Security Group Product Template. Feel free to customize it based on your specific requirements and provide additional instructions or examples as needed.