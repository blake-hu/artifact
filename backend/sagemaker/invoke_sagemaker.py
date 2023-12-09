import boto3
import json
import base64

runtime = boto3.client("sagemaker-runtime")

endpoint_name = "artifact-v6"
content_type = "application/json"

with open("./deploy_test/ai.jpg", 'rb') as image_file:
    # Encode the binary data as base64
    base64_encoded_image = base64.b64encode(image_file.read()).decode()

# Define the input data as a dictionary
input_data = {
    "image": base64_encoded_image
}

# Convert the input data to JSON
input_json = json.dumps(input_data)

try:
    print('invoking')
    # Invoke the SageMaker endpoint
    response = runtime.invoke_endpoint(
        EndpointName=endpoint_name,
        ContentType='application/json',
        Body=input_json
    )
    print('invoked')

    # Parse the response
    result = response['Body'].read().decode('utf-8')
    result = json.loads(result)

    # Print or process the result
    print(result)

except Exception as e:
    print(f"Error invoking SageMaker endpoint: {str(e)}")
