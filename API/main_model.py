import cv2
import difflib
import numpy as np
import keras.backend as K
from keras.models import load_model
import sys

model = None
char_list = "!\"#&'()*+,-./0123456789:;?ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

def load_model_once():
    global model
    if model is None:
        model = load_model('Text_recognizer_Using_CRNN_act.h5', compile=False)
    return model

def process_image(img):
    """
    Converts image to shape (32, 128, 1) & normalize
    """
    w, h = img.shape

    new_w = 32
    new_h = int(h * (new_w / w))
    img = cv2.resize(img, (new_h, new_w))
    w, h = img.shape

    img = img.astype('float32')

    if w < 32:
        add_zeros = np.full((32-w, h), 255)
        img = np.concatenate((img, add_zeros))
        w, h = img.shape

    if h < 128:
        add_zeros = np.full((w, 128-h), 255)
        img = np.concatenate((img, add_zeros), axis=1)
        w, h = img.shape

    if h > 128 or w > 32:
        dim = (128,32)
        img = cv2.resize(img, dim)

    img = cv2.subtract(255, img)
    img = np.expand_dims(img, axis=-1)
    img = img / 255

    img = np.expand_dims(img, axis=0)

    return img

def find_closest_medicine(user_input):
    closest_match = None
    highest_ratio = 0
    medicine_list = None

    with open("medicine_names.txt", "r") as file:
        medicine_list = file.read().splitlines()

    for medicine in medicine_list:
        similarity_ratio = difflib.SequenceMatcher(None, user_input.lower(), medicine.lower()).ratio()
        if similarity_ratio > highest_ratio:
            highest_ratio = similarity_ratio
            closest_match = medicine

    return closest_match, highest_ratio

def predict_text(image_path):
    model = load_model_once()
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    img = process_image(image)
    prediction = model.predict(img)
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

if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage: python main_model.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    predicted_text = predict_text(file_path)
    closest_med, probability = find_closest_medicine(predicted_text)
    print(f"{closest_med} || {probability:.2f}")
