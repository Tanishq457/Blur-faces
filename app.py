

import sys
from flask import Flask, render_template, request, url_for, redirect, session
from flask.helpers import flash
from werkzeug.utils import secure_filename

import os
import numpy as np
import cv2
import matplotlib.pyplot as plt
import json

filename2 = ''
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['png', 'png', 'jpg', 'jpeg', 'webp'])

app = Flask(__name__)


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    global filename2
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

@app.route('/result', methods=['GET'])
def result():
    messages = request.args['messages']  # counterpart for url_for()
    messages=json.loads(messages)
    print("###############" + str(messages), file=sys.stdout)
    # print(messages[0], file=sys.stdout)
    # print(messages[1], file=sys.stdout)

    return render_template('result.html', no_faces = messages['no_faces'], photo = messages['name'])

# Result page - on form submit
@app.route('/blur',methods=['GET', 'POST'])
def check():
    faces = ''
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename2 = filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            
            
            
            image = cv2.imread(UPLOAD_FOLDER + '/' + filename2)
        
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            face_detect = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt.xml')
            face_data = face_detect.detectMultiScale(image, 1.3, 5)
            faces = len(face_data)
            for (x, y, w, h) in face_data:
                print("Values: ", x, y, w, h)
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                roi = image[y:y+h, x:x+w]

                roi = cv2.GaussianBlur(roi, (23, 23), 30)

                image[y:y+roi.shape[0], x:x+roi.shape[1]] = roi
            
            full_filename = os.path.join('results', filename2)
            print(full_filename, file=sys.stdout)

            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            cv2.imwrite(full_filename, image)

            messages = json.dumps({"no_faces":faces, "name":full_filename})
            return redirect(url_for('.result', messages=messages))
    return '<html><head><title>Loading</title></head><body>Loading</body></html>'

if __name__ == '__main__':
	app.run(debug=True)
  