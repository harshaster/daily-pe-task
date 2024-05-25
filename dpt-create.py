import boto3
import json
import re
import uuid
import datetime

table = 'dailype-task'
manager_table = 'dailype-task-manager'

user_table = boto3.resource('dynamodb').Table(table)
manager_table = boto3.resource('dynamodb').Table(manager_table)


def lambda_handler(event:dict, context):

    event_data = event.get('body')
    if(type(event_data)==str):
        event_data = json.loads(event_data)
    full_name:str = event_data.get('full_name')
    mob_num:str = event_data.get('mob_num')
    pan_num:str = event_data.get('pan_num')
    manager_id:uuid = None
    if(event_data.get('manager_id')):
        manager_id:uuid = event_data['manager_id']
    
    if (not full_name):
        return {
            "status" : "error",
            "error" : "Full Name is required"
        }
    
    if (not mob_num):
        return {
            "status" : "error",
            "error" : "Mobile Number is required"
        }
    else:
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
        
    if (not pan_num):
        return {
            "status" : "error",
            "error" : "PAN Number is required"
        }
    else:
        pan_num = pan_num.upper()
        if (not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', pan_num)):
            return {
                "status" : "error",
                "error" : "Invalid PAN Number"
            }
        
    if(manager_id):
        manager = manager_table.get_item(Key={"uuid": manager_id}).get('Item')
        if(not manager):
            return {
                "status" : "error",
                "error" : "Manager not found"
            }
        
    userData = {
        'id': str(uuid.uuid4()),
        'full_name': full_name,
        'mob_num': mob_num,
        'pan_num': pan_num,
        'manager-id': manager_id,
        "created_at": str(datetime.datetime.now()),
        "updated_at": None,
        "is_active": True
    }

    user_table.put_item(Item=userData)
    return {
        "status" : "success",
        "data" : userData
    }

