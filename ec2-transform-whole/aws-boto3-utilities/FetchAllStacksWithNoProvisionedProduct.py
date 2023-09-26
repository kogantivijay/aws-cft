import boto3

# Initialize Boto3 clients
cf_client = boto3.client('cloudformation')
sc_client = boto3.client('servicecatalog')

# List all CloudFormation Stacks
stacks = []
paginator = cf_client.get_paginator('list_stacks')
for page in paginator.paginate(StackStatusFilter=['CREATE_COMPLETE', 'UPDATE_COMPLETE']):
    for stack in page['StackSummaries']:
        stacks.append(stack['StackName'])

# List all Provisioned Products
provisioned_products = []
paginator = sc_client.get_paginator('list_provisioned_products')
for page in paginator.paginate():
    for product in page['ProvisionedProducts']:
        provisioned_products.append(product['PhysicalId'])

# Filter out CloudFormation Stacks that have an associated provisioned product
stacks_without_products = [stack for stack in stacks if stack not in provisioned_products]

# Output the result
print(stacks_without_products)

# Optionally, write the result to a file
with open('stacks_without_products.txt', 'w') as f:
    for stack in stacks_without_products:
        f.write(f"{stack}\n")
