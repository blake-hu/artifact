import json
import boto3
import os
import uuid
import base64
import pathlib

from configparser import ConfigParser

def lambda_handler(event, context):
  try:
    print("**STARTING**")
    
    #
    # setup AWS based on config file:
    #
    config_file = 'config.ini'
    os.environ['AWS_SHARED_CREDENTIALS_FILE'] = config_file
    
    configur = ConfigParser()
    configur.read(config_file)
    
    #
    # configure for S3 access:
    #
    s3_profile = 's3readwrite'
    boto3.setup_default_session(profile_name=s3_profile)
    
    bucketname = configur.get('s3', 'bucket_name')
    
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucketname)
    
  
    #
    # the user has sent us two parameters:
    #  1. filename of their file
    #  2. raw file data in base64 encoded string
    #
    # The parameters are coming through web server 
    # (or API Gateway) in the body of the request
    # in JSON format.
    #
    print("**Accessing request body**")
    
    if "body" not in event or not event["body"]:
      print("Request body is empty or not provided")
      return {
        'statusCode': 400,
        'body': "Bad request: empty or missing body"
    }
      
    body = json.loads(event["body"]) # parse the json
    
    if "filename" not in body:
      raise Exception("event has a body but no filename")
    if "data" not in body:
      raise Exception("event has a body but no data")

    filename = body["filename"]
    datastr = body["data"]
    
    print("filename:", filename)
    print("datastr (first 10 chars):", datastr[0:10])

    
    #
    # upload to S3:
    #
    base64_bytes = datastr.encode()        # string -> base64 bytes
    bytes = base64.b64decode(base64_bytes) # base64 bytes -> raw bytes
    
    #
    # write raw bytes to local filesystem for upload:
    #
    print("**Writing local data file**")
    
    local_filename = "/tmp/data.pdf"
    
    outfile = open(local_filename, "wb")
    outfile.write(bytes)
    outfile.close()
    
    #
    # generate unique filename in preparation for the S3 upload:
    #
    print("**Uploading local file to S3**")
    
    basename = pathlib.Path(filename).stem
    extension = pathlib.Path(filename).suffix
    
    bucketkey = filename+ str(uuid.uuid4())+ "."+ extension
    
    
    print("S3 bucketkey:", bucketkey)
    
    #
    # finally, upload to S3:
    #
    print("**Uploading data file to S3**")

    bucket.upload_file(local_filename, 
                       bucketkey, 
                       ExtraArgs={
                         'ACL': 'public-read',
                         'ContentType': 'application/pdf'
                       })

    #
    # respond in an HTTP-like way, i.e. with a status
    # code and body in JSON format:
    #
    print("**DONE**")
    
    return {
      'statusCode': 200,
      'body': "upload_complete"
    }
    
  except Exception as err:
    print("**ERROR**")
    print(str(err))
    
    return {
      'statusCode': 400,
      'body': "upload_complete"
    }
