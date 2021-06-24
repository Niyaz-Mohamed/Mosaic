#from flask import Flask
#from flask import render_template, request, flash, request, redirect, url_for
from flask import *
from werkzeug.exceptions import HTTPException
from werkzeug.utils import secure_filename
from PIL import Image
import skimage

import os, json
import urllib.request

#Run c:/Users/niyaz/Desktop/Projects/Apps/mosiac/env/Scripts/activate.bat to activate venv
UPLOAD_FOLDER='./static/uploads/'
ALLOWED_EXTENSIONS={'png','jpg','jpeg'}
CURRENT_IMAGE_DATA={'filename':'','width':0,'height':0}

app=Flask(__name__)
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
app.config['CURRENT_IMAGE_DATA']=CURRENT_IMAGE_DATA

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowedFile(filename):
    allowedExtensions = set(['png','jpg','jpeg'])
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowedExtensions

@app.errorhandler(HTTPException)
def handle_exception(e):
    error = {'code':e.code,'name':e.name,'description':e.description}
    return render_template('error.html', error=error)

@app.route('/')
def baseRedirect():
    return redirect('home')

@app.route('/home')
def root():

    title_desc="""Mosiac allows you to take a high-definition image and convert it to pixel art.\n 
    It provides features to freely control the degree of pixelization, make an image greyscale, 
    or change the palette used by the image."""

    return render_template('index.html',title_desc=title_desc)

@app.route('/base')
def loadBase():
    return render_template('base.html',noLoadFooter=True)

@app.route('/editor',methods=['POST','GET'])
def runEditor():

    filename=''
    errorMsg='No file chosen'

    if request.method == 'POST':
        
        try:
            if 'file' not in request.files:
                errorMsg='Error: Form did not return Image'
                flash('No file part')
                return redirect(request.url)
                
            file=request.files['file']

            if file.filename =='':
                errorMsg='Error: No file chosen'
                flash('No selected file')
                return redirect(request.url)
                
            if file and allowed_file(file.filename):
                filename=secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
                #CARRY OUT IMAGE PROCESSING HERE

        except:
            errorMsg='Error: Please try again'

    if os.path.isfile(app.config['UPLOAD_FOLDER']+filename):

        #DO IMAGE PROCESSING IF IMAGE EXISTS
        img=Image.open(r''+app.config['UPLOAD_FOLDER']+filename)

        #SET VALUES TO PASS TO render_template()
        app.config['CURRENT_IMAGE_DATA']['filename']=filename
        app.config['CURRENT_IMAGE_DATA']['width']=(img.size)[0]
        app.config['CURRENT_IMAGE_DATA']['height']=(img.size)[1]

    return render_template('editor.html',
    filename=app.config['CURRENT_IMAGE_DATA']['filename'],
    width=app.config['CURRENT_IMAGE_DATA']['width'],
    height=app.config['CURRENT_IMAGE_DATA']['height'],
    errorMsg=errorMsg
    )

@app.route('/library')
def imageLib():
    return render_template('library.html')

app.run(host='0.0.0.0', port=8080, debug=True)

#TODO: 
#Test image form