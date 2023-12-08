import torch
from PIL import Image
import numpy as np
from model import CNN
import flask
from flask import Flask, request, jsonify
import base64
import io

app = flask.Flask(__name__)


@app.route('/ping', methods=["GET", "POST"])
def ping():
    return '', 200


@app.route('/invocations', methods=["POST"])
def invoke():
    data = request.get_json()

    if data is None:
        return jsonify({'error': 'No JSON data provided'}), 400

    base64_image = data["image"]

    image_bytes = base64.b64decode(base64_image)

    # Create a BytesIO object from the decoded bytes
    image_buffer = io.BytesIO(image_bytes)

    image = Image.open(image_buffer)

    # model() is a hypothetical function that gets the inference output:
    prob = predict(image)

    return jsonify({"probability_real": prob}), 200


def predict(image_raw):

    device = torch.device("cpu")

    # Open the image using Pillow
    image_resized = image_raw.resize((32, 32))

    # Convert the image to a NumPy array
    image = np.array(image_resized)
    image = torch.tensor(image, dtype=torch.float32) / 255.0
    image = image.transpose(1, 2).transpose(0, 1).unsqueeze(0)
    image = image.to(device)

    model = CNN()
    model.load_state_dict(torch.load("./model_state_dict.pt",
                                     map_location=torch.device('cpu')))
    model.to(device)

    model.eval()
    sigmoid = torch.nn.Sigmoid()
    with torch.no_grad():
        image = image.to(device)
        logit = model(image)
        prob = sigmoid(logit)
        return prob.item()


if __name__ == '__main__':
    app.run(port=8080, debug=True)
