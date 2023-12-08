import json
import boto3
import os
import uuid
import base64
import pathlib
import datatier
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
    # configure for RDS access
    #
    rds_endpoint = configur.get('rds', 'endpoint')
    rds_portnum = int(configur.get('rds', 'port_number'))
    rds_username = configur.get('rds', 'user_name')
    rds_pwd = configur.get('rds', 'user_pwd')
    rds_dbname = configur.get('rds', 'db_name')

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
    
    # upload to S3:
    #
    filename = body["filename"]
    datastr = body["data"]
    
    print("filename:", filename)
    print("datastr (first 10 chars):", datastr[0:10])
    base64_bytes = datastr.encode()        # string -> base64 bytes
    bytes = base64.b64decode(base64_bytes) # base64 bytes -> raw bytes
    
    #
    # write raw bytes to local filesystem for upload:
    #
    print("**Writing local data file**")
    
    extension = pathlib.Path(filename).suffix
    local_filename = "/tmp/data"+extension
    
    # allow only png and jpeg extension types
    content_types = {
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    }
    print("extension:",extension)
    
    # return with error if incorrect type
    if extension in content_types:
       content_type = content_types[extension]
    else:
      return {
      'statusCode': 400,
      'body': json.dumps("Incorrect File Type")
      }
    
    outfile = open(local_filename, "wb")
    outfile.write(bytes)
    outfile.close()
    
    #
    # generate unique filename in preparation for the S3 upload:
    # all inputed images with same input extension for the trigger to work
    #
    print("**Uploading local file to S3**")
    
    basename = pathlib.Path(filename).stem
    bucketkey = "inputImages" +"/"+filename +"-"+ str(uuid.uuid4())+ extension
    
    print("S3 bucketkey:", bucketkey)
    
    #
    # finally, upload to S3:
    #
    print("**Uploading data file to S3**")

    bucket.upload_file(local_filename, 
                       bucketkey, 
                       ExtraArgs={
                         'ACL': 'public-read',
                         'ContentType': content_type,
                       })
                       
    # open connection to the database:
    #
    print("**Opening connection**")
    
    dbConn = datatier.get_dbConn(rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname)

    # add the records into databases
    #
    print("**Adding row to database**")

    sql1="""
    INSERT INTO imageMetadata(image_size, file_name, bucket_key)
    values(%s, %s,%s);"""

    datatier.perform_action(dbConn, sql1, [os.path.getsize(local_filename), filename, bucketkey])

    sql2 = "SELECT LAST_INSERT_ID();"
    
    row = datatier.retrieve_one_row(dbConn, sql2)
    
    imageID = row[0]
    
    print("imageID:", imageID)
    
    sql3="""
    INSERT INTO imagePredictions(image_id, precentage_ai, status, model_version) values(%s,0,'pending',1);"""
    datatier.perform_action(dbConn, sql3, [imageID])
    
    # respond in an HTTP-like way, i.e. with a status
    # code and body in JSON format:
    #
    print("**DONE**")
    
    response={
      'statusCode': 200,
      'body': json.dumps({'imageID': imageID})
    }
    print("API Response:", response)
    return response
    
    
  except Exception as err:
    print("**ERROR**")
    print(str(err))
    
    return {
      'statusCode': 400,
      'body': "uh-oh, something went wrong"
    }