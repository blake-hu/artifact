import boto3
import json
import os
import base64
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
        # configurefor permissions
        #
        s3_profile = 'blake' 
        boto3.setup_default_session(profile_name=s3_profile)

        #
        # configure for RDS access
        #
        rds_endpoint = configur.get('rds', 'endpoint')
        rds_portnum = int(configur.get('rds', 'port_number'))
        rds_username = configur.get('rds', 'user_name')
        rds_pwd = configur.get('rds', 'user_pwd')
        rds_dbname = configur.get('rds', 'db_name')

        
        # get bucket and key of what triggered this compute call
        s3_bucket = event['Records'][0]['s3']['bucket']['name']
        s3_key = event['Records'][0]['s3']['object']['key']

        s3_client = boto3.client('s3')
        
        try:
            # encode the image into json format 
            response = s3_client.get_object(Bucket=s3_bucket, Key=s3_key)
            image_data = response['Body'].read()
            encoded_image = base64.b64encode(image_data).decode('utf-8')
            input_data= {"image": encoded_image}
            input_json = json.dumps(input_data)
            print(input_json)
            
        except Exception as e:
            print(f"Error downloading image from S3: {e}")
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Internal Server Error'})
            }
        
        # send the image to the sagemaker endpoint
        
        sage_maker_endpoint_name = 'artifact-v6'
        sagemaker_runtime = boto3.client('sagemaker-runtime')
        try:
            response = sagemaker_runtime.invoke_endpoint(
                EndpointName=sage_maker_endpoint_name,
                ContentType= "application/json",
                Body=input_json
            )

            # Process the prediction result as needed
            prediction_result = json.loads(response['Body'].read().decode())
            actual_prob= 100*(1-prediction_result["probability_real"])
            print("Probability of ai image:", actual_prob)

        except Exception as e:
            print(f"Error invoking SageMaker endpoint: {e}")
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Internal Server Error'})
            }
            
        # put the probability into database and update status
        dbConn = datatier.get_dbConn(rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname)

    
        sql1 = "SELECT image_id FROM imageMetadata WHERE bucket_key = %s";
    
        row = datatier.retrieve_one_row(dbConn, sql1, [s3_key])
        image_id= row[0]
        print("image id",image_id)
    
        sql2 = "UPDATE imagePredictions SET precentage_ai = %s, status = %s WHERE image_id = %s";
    
        # update: status is complete and percentage is accurate
    
        datatier.perform_action(dbConn, sql2, [actual_prob, "complete",image_id])
        
        return {
        'statusCode': 200,
        'body': actual_prob
        }
    
    except Exception as err:
        print("**ERROR**")
        print(str(err))
        
        return {
        'statusCode': 400,
        'body': "compute_complete"
        }