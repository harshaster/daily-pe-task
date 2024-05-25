import boto3
import json

table = 'dailype-task'

dynamodb = boto3.resource('dynamodb').Table(table)

def lambda_handler(event, context):
    return event
