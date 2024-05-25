import boto3
import json
from boto3.dynamodb.conditions import Key, Attr

table = 'dailype-task'

user_table = boto3.resource('dynamodb').Table(table)

def lambda_handler(event,context):
    # get all users from the table
    event_data = event.get('body')
    if(type(event_data)==str):
        event_data = json.loads(event_data)
    if(not event_data):
        event_data = {}
    if(event_data.get('id')):
        response = user_table.get_item(
            Key={
                'id': event_data['id']
            }
        )
        if('Item' in response):
            return {
                'status' : 'success',
                'users' : [response['Item']]
            }
        else:
            return {}
    
    if(event_data.get('mob_num')):
        response = user_table.scan(
            FilterExpression = Key('mob_num').eq(event_data['mob_num'])
        )
        if('Items' in response):
            return {
                'status' : 'success',
                'users' : response['Items']
            }
        else:
            return {}
        
    if(event_data.get('manager_id')):
        response = user_table.scan(
            FilterExpression = Key('manager_id').eq(event_data['manager_id'])
        )
        if('Items' in response):
            return {
                'status' : 'success',
                'users' : response['Items']
            }
        else:
            return {}

    response = user_table.scan()
    users = response['Items']
    if(len(users)==0):
        return {}
    else:
        return {
            'status' : 'success',
            'users' : users
        }
    
    
    