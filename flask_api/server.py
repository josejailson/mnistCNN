from flask import Flask, request, render_template
from PIL import Image
import tensorflow as tf
import numpy as np


json_file = open('model.json', 'r')
model_json = json_file.read()
json_file.close()
model = tf.keras.models.model_from_json(model_json)

model.load_weights("weights.h5")
model.compile(loss="categorical_crossentropy", 
              optimizer="adam", 
              metrics=["accuracy"])

graph = tf.compat.v1.get_default_graph()


app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")


import re
import base64

def stringToImage(img):
    imgstr = re.search(r'base64, (.*)', str(img)).group(1)
    with open('image.png', 'wb') as output:
        output.write(base64.b64decode(imgstr))

@app.route('/predict/', methods=["POST"])
def predict():
    global model, graph
    imgData = request.get_data()
    try:
        stringToImage(imgData)
    except:
        f = request.files['img']
        f.save('image.png')
    x = Image.open('image.png').convert('L')
    x = x.resize((28,28))
    x = np.array(x)
    x = x.reshape(1, (28, 28), 1)

    with graph.as_default():
        prediction = model.predict(x)
        response = np.argmax(prediction, axis=1)
        return str(response[0])
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
    app.run(debug=True)

