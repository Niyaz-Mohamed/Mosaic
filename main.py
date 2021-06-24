from flask import Flask
from flask import render_template, request, flash, request, redirect, url_for
from werkzeug.exceptions import HTTPException
from werkzeug.utils import secure_filename

import os, json
import urllib.request

UPLOAD_FOLDER='./static/uploads'
ALLOWED_EXTENSIONS={'png','jpg','jpeg'}

app=Flask(__name__)
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER

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
            print('request called')
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
                print(filename)
                try:
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
                except:
                    errorMsg('Error: Image Upload Failed')
        except:
            errorMsg='Error: Please try again'

    return render_template('editor.html',filename=filename,errorMsg=errorMsg)

@app.route('/library')
def imageLib():
    return render_template('library.html')

app.run(host='0.0.0.0', port=8080, debug=True)

#TODO: 
#Test image form