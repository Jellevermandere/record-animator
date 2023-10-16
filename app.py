# README
# To start the server in development mode run:
# flask --app app run --host=0.0.0.0

import os
import numpy as np
import cv2
from flask import Flask, flash, request, redirect, url_for, render_template, make_response, send_file
from werkzeug.utils import secure_filename
import requests
import recordcreator as rc
from PIL import ImageColor
import io

UPLOAD_FOLDER = "/rawData"
ALLOWED_EXTENSIONS = {'png', 'PNG'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Global variables
dirname = os.path.dirname(__file__)


# The main page to show stuff 
@app.route("/")
def index():
    return render_template('index.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Create a sub selection of the data with given global coordinates
@app.route("/recordmaker", methods=['GET', 'POST'])
def add_session():
    if request.method == 'POST':
        
        print(request.files)
        print(request.form)

        # check if the post request has the file part
        if 'file' not in request.files:
            print('No file part in files')
            return redirect(request.url)

        uploaded_files = request.files.getlist("file")
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if len(uploaded_files) == 0:
            print('File array is empty')
            return redirect(request.url)
        else:
            images = []
            nrOfImages = 0
            for file in uploaded_files:
                file_bytes = np.fromfile(file, np.uint8)
                imageFile = cv2.imdecode(file_bytes, cv2.IMREAD_UNCHANGED)
                nrOfImages +=1
                #print(imageFile.shape)
                images.append(imageFile)

            bgColor = request.form.get("favcolor")
            bgColorRgb = ImageColor.getcolor(bgColor, "RGB")
            blankRecordSize = int(images[0].shape[0]*2)
            img = rc.create_blank_record(blankRecordSize, bgColorRgb)
            result = rc.place_pies(img, images)
            result = cv2.cvtColor(result, cv2.COLOR_BGRA2RGBA)
            if(request.form.get("gif")):
                rc.save_record_gif(result, nrOfImages, "output/animatedRecord.gif")
                return send_file('output/animatedRecord.gif')
            retval, buffer = cv2.imencode('.png', result)
            response = make_response(buffer.tobytes())
            response.headers['Content-Type'] = 'image/png'
            print("Upload Success")
            return response
    else:
        return render_template('recordmaker.html')
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)