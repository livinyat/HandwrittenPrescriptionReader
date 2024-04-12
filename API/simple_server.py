import http.server
import socketserver
import json
import cv2
import numpy as np
from main_model import process_image, load_model_once
import keras.backend as K

PORT = 8000
char_list = "!\"#&'()*+,-./0123456789:;?ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

def get_predicted_text(image, model):
    # Preprocess the input image
    img = process_image(image)
    # Perform prediction
    prediction = model.predict(img)
    # Perform CTC decoding to get the predicted text
    decoded = K.ctc_decode(prediction,
                           input_length=np.ones(prediction.shape[0]) * prediction.shape[1],
                           greedy=True)[0][0]
    out = K.get_value(decoded)
    predicted_text = ''
    for i, x in enumerate(out):
        for p in x:
            if int(p) != -1:
                predicted_text += char_list[int(p)]
    return predicted_text

class PredictionHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        data = self.rfile.read(content_length)
        
        # Convert the received binary data to a numpy array
        nparr = np.frombuffer(data, np.uint8)
        
        # Decode the numpy array into an image
        image = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

        # Get the predicted text
        predicted_text = get_predicted_text(image, self.server.model)

        # Respond with the predicted text
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {'predicted_text': predicted_text}
        self.wfile.write(json.dumps(response).encode())

def run_server():
    with socketserver.TCPServer(("", PORT), PredictionHandler) as httpd:
        print("Server started on port", PORT)
        httpd.model = load_model_once()  # Load the model
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()
