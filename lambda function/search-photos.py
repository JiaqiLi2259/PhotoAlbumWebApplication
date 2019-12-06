import json
import boto3
import os
import sys
import uuid
import time
# import requests
from botocore.vendored import requests

ES_HOST = 'YOUR ES ENDPOINT'
ES_INDEX = 'photos'
ES_TYPE = 'Photo'
PHOTOS_BUCKET = 'photoalbumb2'
BUCKET_REGION = 'us-west-2'
LEX_NAME = 'SmartPhotoBot'
LEX_ALIAS = 'bota'
headers = {"Content-Type": "application/json"}

def lambda_handler(event, context):
    print("#TEST# The whole event is shown below:")
    print(event)
    query = event["query"]
    query = str(query).lower()
    lex_client = boto3.client('lex-runtime')
    lex_response = lex_client.post_text(
        botName=LEX_NAME,
        botAlias=LEX_ALIAS,
        userId='Jackie',
        inputText=query
    )
    slots = lex_response['slots']
    print("#TEST# Slots in LEX response:")
    print(slots)
    img_url_list = []
    for slot_name, tag in slots.items():
        print("#TEST# tags of {}:".format(slot_name))
        print(tag)
        if tag is not None:
            url = get_es_url(tag)
            print("#TEST# url of ES:")
            print(url)
            es_response = requests.get(url, headers=headers).json()
            print("#TEST# ES response")
            print("{}".format(json.dumps(es_response)))
            es_src = es_response['hits']['hits']
            print("ES HITS --- {}".format(json.dumps(es_src)))
            for photo in es_src:
                labels = [word.lower() for word in photo['_source']['labels']]
                if tag in labels:
                    objectKey = photo['_source']['objectKey']
                    img_url = get_img_url(objectKey)
                    img_url_list.append(img_url)
    
    return {
        'statusCode': 200,
        'body': json.dumps(img_url_list)
    }
    

def get_es_url(key):
    url = ES_HOST + '/' + ES_INDEX + '/' + ES_TYPE + '/_search?q=' + key.lower()
    return url

def get_img_url(key):
    # url = 'https://' + PHOTOS_BUCKET + '.s3.amazonaws.com/' + key
    url = "https://" + PHOTOS_BUCKET + ".s3-" + BUCKET_REGION +".amazonaws.com/" + key
    return url
    
def getDynamicUrl(num):
    url = "YOUR PHOTOS_BUCKET ENDPOINT";
    url = url + String(num) + ".jpg";
    return url;