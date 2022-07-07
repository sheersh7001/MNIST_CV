from flask import Flask, render_template, redirect, flash, request
import os
from werkzeug.utils import secure_filename
ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg']
UPLOADS_FOLDER = 'uploads/images/'
def file_valid(file):
    return '.' in file and \
        file.rsplit('.',1)[1] in ALLOWED_EXTENSIONS
app = Flask(__name__)
app.config['SECRET_KEY'] = 'asldjbsanfjikbwodlakn123!@'
app.config['UPLOADS_FOLDER'] = UPLOADS_FOLDER

import numpy as np
import cv2
def resize_to_28x28(img):
    img_h, img_w = img.shape
    dim_size_max = max(img.shape)

    if dim_size_max == img_w:
        im_h = (26 * img_h) // img_w
        if im_h <= 0 or img_w <= 0:
            print("Invalid Image Dimention: ", im_h, img_w, img_h)
        tmp_img = cv2.resize(img, (26,im_h),0,0,cv2.INTER_NEAREST)
    else:
        im_w = (26 * img_w) // img_h
        if im_w <= 0 or img_h <= 0:
            print("Invalid Image Dimention: ", im_w, img_w, img_h)
        tmp_img = cv2.resize(img, (im_w, 26),0,0,cv2.INTER_NEAREST)

    out_img = np.zeros((28, 28), dtype=np.ubyte)

    nb_h, nb_w = out_img.shape
    na_h, na_w = tmp_img.shape
    y_min = (nb_w) // 2 - (na_w // 2)
    y_max = y_min + na_w
    x_min = (nb_h) // 2 - (na_h // 2)
    x_max = x_min + na_h

    out_img[x_min:x_max, y_min:y_max] = tmp_img

    return out_img

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template('index.html')
    if not 'file' in request.files:
        flash('No file part in request')
        return redirect(request.url)
    file = request.files.get('file')
    if file.filename == '':
        flash('No file Uploaded')
        return redirect(request.url)
    if file_valid(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOADS_FOLDER'],filename))
        file_path = os.path.join(app.config['UPLOADS_FOLDER'],filename)
        check_img = cv2.imread(file_path,cv2.IMREAD_GRAYSCALE)
        newImg = resize_to_28x28(check_img)/(255.0)
        reimg = newImg.reshape(-1)
        print(type(reimg))
        input_data_extracted = '{"data": [' + str(list(reimg)) + "]}"
        import requests
        scoring_uri = 'http://1a70ae16-a162-4de4-aca9-3213db94ce17.eastus2.azurecontainer.io/score'
        headers = {'Content-Type': 'application/json'}
        resp = requests.post(scoring_uri, input_data_extracted, headers=headers)
        result = resp.text
        return f'The number in the Image is {result}'
    return render_template('index.html')