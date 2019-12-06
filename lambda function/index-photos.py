import json
import boto3
import os
import sys
import uuid
from botocore.vendored import requests
from datetime import *

ES_HOST = 'YOUR ES HOST'
REGION = 'us-west-2'
es_endpoint = 'YOUR ES ENDPOINT'
es_index = 'photos'
es_type = 'Photo'

def lambda_handler(event, context):
    print('#TEST# Event is shown below:')
    print("{}".format(json.dumps(event)))
    rek_client = boto3.client('rekognition')
    headers = { "Content-Type": "application/json" }
    for single_record in event['Records']:
        JSON_object = {}
        bucket_name = single_record['s3']['bucket']['name']
        image_key = single_record['s3']['object']['key']
        rek_response = rek_client.detect_labels(
            Image={
                'S3Object': {
                    'Bucket': bucket_name,
                    'Name': image_key,
                },
            },
            MaxLabels=123,
            MinConfidence=70,
        )
        if rek_response is not None:
            JSON_object['objectKey'] = image_key
            id = JSON_object['objectKey']
            JSON_object["bucket"] = bucket_name
            JSON_object["createdTimestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            JSON_object["labels"] = []
            labels = rek_response['Labels']
            print('#TEST# Label Attribute of Rekognition are shown below:')
            print(labels)
            for label in labels:
                JSON_object["labels"].append(label['Name'])
            print('#TEST# Json Object:')
            print("{}".format(JSON_object))
            
            url = ES_HOST + '/' + 'photos' + '/' + 'Photo'
            print("#TEST# URL of ES")
            print("{}".format(url))
            JSON_object = json.dumps(JSON_object)
            url = es_endpoint + '/' + es_index + '/' + es_type + '/'
            req = requests.post(url + str(id), data=JSON_object, headers=headers)
            print("#TEST# response form ES is:")
            print(req)
            
    
    return {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Origin": "*",
            'Content-Type': 'application/json'
        },
        'body': json.dumps("Image labels have been successfully detected!")
    }
