import json
import random
from crhelper import CfnResource

helper = CfnResource()

@helper.create
@helper.update
def create_update(event, context):
    print('Received event:', json.dumps(event))
    response_data = {"randomNumber": str(random.randint(1, 100))}
    helper.Data.update(response_data)

@helper.delete
def delete(event, context):
    pass

def handler(event, context):
    helper(event, context)