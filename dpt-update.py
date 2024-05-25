import boto3
from boto3.dynamodb.conditions import Key
import json
from datetime import datetime
import re

table = 'dailype-task'
user_table = boto3.resource('dynamodb').Table(table)
manager_table = boto3.resource('dynamodb').Table('dailype-task-manager')

def lambda_handler(event,context):

    def checkUserexist(id):
        exists = user_table.get_item(
            Key={
                'id': id
            }
        )
        if('Item' in exists):
            return True
        else:
            return False

    event_data = event.get('body')
    if(type(event_data)==str):
        event_data = json.loads(event_data)
    if(not event_data):
        event_data = {}
        return {
            'status' : 'error',
            'error' : 'No data provided'
        }
    
    user_ids = event_data.get('user_ids')
    update_data = event_data.get('update_data')
    for id in user_ids:
        if(not checkUserexist(id)):
            return {
                'status' : 'error',
                'error' : 'User with id '+id+' does not exist'
            }

    if(len(user_ids)>1):
        for k in update_data.keys():
            if k in ['mob_num', 'pan_num', 'full_name']:
                return {
                    'status' : 'error',
                    'error' : 'These keys can be updated on a individual basis only and not in bulk'
                }
        
        if 'manager_id' in update_data:
            manager_exists = manager_table.get_item(
                Key={
                    'id': update_data['manager_id']
                }
            )
            if('Item' not in manager_exists):
                return {
                    'status' : 'error',
                    'error' : 'Manager does not exist'
                }
            
        for id in user_ids:
            # If the manager_id is being updated, for the first time just insert the manager_id against the user and then add the updated_at, but if the user already has a manager then the current database entry should be made is_active = false, and a new entry for the user should be created with its old data but the new manager_id and updated timestamps.
            userData = user_table.get_item(
                Key={
                    'id': id
                }
            )['Item']
            if not userData.get('manager_id'):
                user_table.update_item(
                    Key={
                        'id': id
                    },
                    UpdateExpression='SET manager_id = :manager_id, updated_at = :updated_at',
                    ExpressionAttributeValues={
                        ':manager_id': update_data['manager_id'],
                        ':updated_at': str(datetime.now())
                    }
                )
            else:
                user_table.update_item(
                    Key={
                        'id': id
                    },
                    UpdateExpression='SET is_active = :is_active',
                    ExpressionAttributeValues={
                        ':is_active': False
                    }
                )
                user_table.put_item(
                    Item={
                        'id': id,
                        'full_name': userData['full_name'],
                        'mob_num': userData['mob_num'],
                        'pan_num': userData['pan_num'],
                        'manager_id': update_data['manager_id'],
                        'created_at': userData['created_at'],
                        'updated_at': str(datetime.now())
                    }
                )
        return {
            'status' : 'success',
            'message' : 'Manager Updated for all users'
        }

    else:
        full_name:str = update_data.get('full_name')
        mob_num:str = update_data.get('mob_num')
        pan_num:str = update_data.get('pan_num')
        print(full_name, mob_num, pan_num)
        if (mob_num):
            if(len(mob_num)>10):
                if(mob_num.startswith('+91')):
                    mob_num = mob_num[3:]
                elif(mob_num.startswith('0')):
                    mob_num = mob_num[1:]
                elif(mob_num.startswith('91')):
                    return {
                        "status" : "error",
                        "error" : "Invalid Country Code. Please put a + before the country code"
                    }
                else:
                    return {
                        "status" : "error",
                        "error" : "Invalid Country Code"
                    }
            if (not re.match(r'^[6-9]\d{9}$', mob_num)):
                return {
                    "status" : "error",
                    "error" : "Invalid Mobile Number"
                }
            
        if (pan_num):
            pan_num = pan_num.upper()
            if (not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', pan_num)):
                return {
                    "status" : "error",
                    "error" : "Invalid PAN Number"
                }
        
        if(not len(full_name)>0):
            return {
                "status" : "error",
                "error" : "Full Name is required"
            }
        

        update_dict = {}
        if full_name:
            update_dict[':full_name'] = full_name
        if mob_num:
            update_dict[':mob_num'] = mob_num
        if pan_num:
            update_dict[':pan_num'] = pan_num
        update_dict[':updated_at'] = str(datetime.now())

        user_table.update_item(
            Key={
                'id': user_ids[0]
            },
            UpdateExpression='SET '+ ','.join([f'{k} = :{k}' for k in update_data.keys()]) + ', updated_at = :updated_at',
            ExpressionAttributeValues=update_dict
        )

        return {
            'status' : 'success',
            'message' : 'User Updated'
        }

    return {
        'status' : 'error',
        'error' : 'Invalid data provided'
    }