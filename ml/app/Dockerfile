# Use an official PyTorch base image
FROM pytorch/pytorch:latest

# Install additional dependencies
RUN pip install Flask
RUN pip install Pillow

# Set the working directory inside the container
WORKDIR /app

# Copy your PyTorch inference script and model files into the container
COPY ./inference.py .
COPY ./model.py .
COPY ./model_state_dict.pt .

# Set the entry point to run your PyTorch inference script
ENTRYPOINT ["python", "inference.py"]