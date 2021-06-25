#from flask import Flask
#from flask import render_template, request, flash, request, redirect, url_for
from flask import *
from werkzeug.exceptions import HTTPException
from werkzeug.utils import secure_filename
from PIL import Image
import skimage

import os, json
import urllib.request

#Activate venv
dir_path=os.path.dirname(os.path.realpath(__file__))
activate_path=os.path.join(dir_path,'./env/Scripts/activate.bat')
os.system(f'py {activate_path}')

UPLOAD_FOLDER='./static/uploads/'
ALLOWED_EXTENSIONS={'png','jpg','jpeg'}
CURRENT_IMAGE=''
CURRENT_IMAGE_DATA={'width':0,'height':0}

app=Flask(__name__)
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
app.config['CURRENT_IMAGE']=CURRENT_IMAGE
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

def pixelate(img,size,pxFactor):

    width=size[0]
    height=size[1]
    
    scaleWidth=round(width*(100-pxFactor)/100)
    scaleHeight=round(height*(100-pxFactor)/100)

    if scaleWidth<1:
        scaleWidth= 1
    if scaleHeight<1:
        scaleHeight= 1
        
    #Scale down by the pxFactor (Ranging from 0 to 100)
    imgSmall = img.resize((scaleWidth,scaleHeight),resample=Image.BILINEAR)
    result = imgSmall.resize(size,Image.NEAREST)
    return result

def greyscale(img):
    return img

def resize(img,newWidth,size):

    oldWidth=size[0]
    oldHeight=size[1]
    newHeight=round(oldHeight*(newWidth/oldWidth))
    img.resize((newWidth,newHeight),resample=Image.BILINEAR)
    return img

@app.route('/editor',methods=['POST','GET'])
def runEditor():

    filename=''
    errorMsg='No file chosen'

    imgConfig=request.form

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
                app.config['CURRENT_IMAGE']=filename

        except:
            errorMsg='Error: Please try again'

    if os.path.isfile(app.config['UPLOAD_FOLDER']+app.config['CURRENT_IMAGE']):
        
        print(app.config['UPLOAD_FOLDER']+app.config['CURRENT_IMAGE'])

        #DO IMAGE PROCESSING IF IMAGE EXISTS

        script_dir= os.path.dirname(__file__) #<-- absolute dir the script is in
        rel_path= os.path.join(app.config['UPLOAD_FOLDER'],app.config['CURRENT_IMAGE'])
        abs_file_path= os.path.join(script_dir, rel_path)
        isolatedFilename=app.config['CURRENT_IMAGE'][:-4]

        img=Image.open(abs_file_path,'r')
        img=pixelate(img=img,size=img.size,pxFactor=int(imgConfig['pixDeg']))
        img=resize(img=img,size=img.size,newWidth=int(imgConfig['newWidth']))
        if 'greyscale' in imgConfig:
            img=greyscale(img)
        if os.path.exists(abs_file_path):
            os.remove(abs_file_path)
        if '_pixelated' not in app.config['CURRENT_IMAGE']:
            img.save(app.config['UPLOAD_FOLDER']+isolatedFilename+'_pixelated'+'.png')
            app.config['CURRENT_IMAGE']=isolatedFilename+'_pixelated'+'.png'
        else:
            img.save(app.config['UPLOAD_FOLDER']+app.config['CURRENT_IMAGE'])
        
        app.config['CURRENT_IMAGE_DATA']['width']=(img.size)[0]
        app.config['CURRENT_IMAGE_DATA']['height']=(img.size)[1]
    
    else:
        app.config['CURRENT_IMAGE']=''

    return render_template('editor.html',
    filename=app.config['CURRENT_IMAGE'],
    width=app.config['CURRENT_IMAGE_DATA']['width'],
    height=app.config['CURRENT_IMAGE_DATA']['height'],
    errorMsg=errorMsg
    )

@app.route('/library')
def imageLib():
    return render_template('library.html')

app.run(host='0.0.0.0', port=8080, debug=True)