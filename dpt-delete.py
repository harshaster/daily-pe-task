import boto3
from boto3.dynamodb.conditions import Key
import json

table = 'users'
user_table = boto3.resource('dynamodb').Table(table)

def lambda_handler(event,context):

    event_data = event.get('body')
    if(type(event_data)==str):
        event_data = json.loads(event_data)
    if(not event_data):
        event_data = {}
        return {
            'status' : 'error',
            'error' : 'No data provided'
        }

    if(event_data.get('id')):
        exists = user_table.get_item(
            Key={
                'id': event_data['id']
            }
        )
        if('Item' in exists):
            user_table.delete_item(
                Key={
                    'id': event_data['id']
                }
            )
            return {
                'status' : 'success',
                'message' : 'User Deleted'
            }
        else:
            return {
                'status' : 'error',
                'error' : 'User does not exist'
            }
    
    if(event_data.get('mob_num')):
        response = user_table.scan(
            FilterExpression = Key('mob_num').eq(event_data['mob_num'])
        )
        if('Items' in response):
            user_table.delete_item(
                Key={
                    'id': response['Items'][0]['id']
                }
            )
            return {
                'status' : 'success',
                'message' : 'User Deleted'
            }
        else:
            return {
                'status' : 'error',
                'error' : 'User does not exist'
            }