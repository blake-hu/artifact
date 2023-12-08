import json
import boto3
import os
import datatier
import base64

from configparser import ConfigParser

def lambda_handler(event, context):
  try:
    print("**STARTING**")
    print("**lambda: retrieve**")

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
    # image_id from event: could be a parameter
    # or could be part of URL path ("pathParameters"):
    if "image_id" in event:
      image_id = event["image_id"]
    elif "pathParameters" in event:
      if "image_id" in event["pathParameters"]:
        image_id = event["pathParameters"]["image_id"]
      else:
        raise Exception("requires image_id parameter in pathParameters")
    else:
        raise Exception("requires image_id parameter in event")
        
    print("image_id:", image_id)

    # open connection to the database:
    #
    print("**Opening connection**")
    
    dbConn = datatier.get_dbConn(rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname)

    #
    # first we need to make sure the userid is valid:
    #
    print("**Checking if image_id is valid**")
    
    sql = "SELECT * FROM imageMetadata WHERE image_id = %s;"
    
    row = datatier.retrieve_one_row(dbConn, sql, [image_id])
    
    if not row:  # no such image
      print("**No such image, returning...**")
      return {
        'statusCode': 400,
        'body': json.dumps("no such image...")
      }
    
    print("image Requested:", image_id)
    time_uploaded= row[1].isoformat() if row[1] else None
    image_size= row[2]
    file_name= row[3]
    bucketkey= row[4]
    
    print("METADATA")
    print(" time uploaded:", time_uploaded)
    print(" image size:", image_size)
    print(" original file name:", file_name)
    print(" bucketkey:", bucketkey)
    
    s3 = boto3.client('s3')

    # Retrieve the image data from S3
    response = s3.get_object(Bucket=bucketname, Key=bucketkey)

    # Extract binary data from the response
    image_binary = response['Body'].read()

    # Encode binary data to base64
    base64_image = base64.b64encode(image_binary).decode('utf-8')
    
    print("image (first 10 chars):", base64_image[0:10])
    
    sql2 = "SELECT * FROM imagePredictions WHERE image_id = %s;"
    
    row2 = datatier.retrieve_one_row(dbConn, sql2, [image_id])
    
    if row2 == ():  # no such image
      print("**No prediction stored, returning...**")
      return {
        'statusCode': 400,
        'body': json.dumps("Something went wrong: no prediction...")
      }
    
    precentage_ai= float(row2[2]) if row2[2] is not None else None
    model_version= row2[3]
    status= row2[4]
    
    print("PREDICTION")
    print(" precentage_ai:", precentage_ai)
    print(" model_version:", model_version)
    print(" status:", status)
    
    results= {
      "time_uploaded": time_uploaded,
      "image_size":image_size,
      "file_name":file_name,
      "precentage_ai":precentage_ai,
      "model_version":model_version,
      "status":status,
      "image":base64_image
    }
    
    if status == 'pending':
      print("**Job status pending, returning...**")
      #
      return {
        'statusCode': 200,
        'body': json.dumps(results)
      }
      
    if status == 'error':
      # return error 
      if results_file_key == "":
        print("**Image status unknown error, returning...**")
        #
        return {
          'statusCode': 400,
          'body': json.dumps("error")
        }
    #
    # either completed or something unexpected:
    #
    if status != "complete":
      print("**Image status unexpected:", status)
      print("**Returning...**")
      #
      msg = "ERROR: unexpected job status: " + status
      #
      return {
        'statusCode': 400,
        'body': json.dumps(msg)
      }
      
    # completed
    return {
    'statusCode': 200,
    'body': json.dumps(results)
    }
    
  except Exception as err:
    print("**ERROR**")
    print(str(err))
    
    return {
      'statusCode': 400,
      'body': json.dumps(str(err))
    }