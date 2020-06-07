import json
import boto3
from datetime import datetime
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth


def lambda_handler(event, context):
    bucket_name = event["Records"][0]["s3"]["bucket"]["name"]
    image_name = event["Records"][0]["s3"]["object"]["key"]
    
    rekognition = boto3.client("rekognition", "us-east-1")
    img = {"S3Object": {"Bucket": bucket_name,"Name": image_name}}
    response = rekognition.detect_labels(Image=img, MaxLabels=50,MinConfidence=90)
    
    obj = []
    #print(response["Labels"][0]["Name"])
    count = 0 
    for i in response["Labels"]:
        obj.append(response["Labels"][count]["Name"])
        count = count+1
        
    #print(obj) 
    
    es_entry= {
        'objectKey':image_name,
        'bucket':bucket_name,
        'createdTimestamp':datetime.now().strftime("%H:%M:%S.%f - %b %d %Y"),
        'labels':obj
    }
    
    print(es_entry)
    region = 'us-east-1'
    service = 'es'
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
    host = 'vpc-photos-plg3qizcqhdnhij3jnpnbpnyaq.us-east-1.es.amazonaws.com'

    es = Elasticsearch(
        hosts=[{'host': host, 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection)

    res = es.index(index="image-data", body=es_entry)
    print(res)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

