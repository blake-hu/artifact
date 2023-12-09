# ArtIfact: Detecting AI-generated Art

## Videos
- Platform Demo: https://youtu.be/CMAa6CjUErY
- Theoretical Background: https://youtu.be/kfeess6JJWk

## backend
The backend processes uploaded images and responds with model predictions. Built with the following technologies:
- AWS Lambda: Request handling, routing to other AWS services
- AWS S3: Store uploaded images and model artifacts
- AWS RDS: Store in-progress jobs and image metadata
- AWS SageMaker: Deploy model for serverless inference
- AWS ECR: Store Docker images containing model inference code

## client
- The client CLI is used to upload images for analysis and retrieve generated predictions.
- Running client.py requires the `requests` library, which can be installed with:
```
pip install requests
```

## ml
- Contains model training notebooks and saved model parameters.
- Machine learning was conducted on the PyTorch deep learning platform.
- Read SETUP.md for instructions for installing dependencies