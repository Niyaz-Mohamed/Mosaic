from flask import Flask
from flask import render_template, request, flash, request, redirect, send_file
from werkzeug.exceptions import HTTPException
from werkzeug.utils import secure_filename
from PIL import Image, ImageOps
import skimage

import os,json
import numpy as np

#Activate venv
dir_path=os.path.dirname(os.path.realpath(__file__))
activate_path=os.path.join(dir_path,'./env/Scripts/activate.bat')
os.system(f'py {activate_path}')

UPLOAD_FOLDER='./static/uploads/'
JSON_UPLOAD_FOLDER='./static/json/'
CURRENT_IMAGE=''
CURRENT_IMAGE_DATA={'width':0,'height':0}
ALLOWED_EXTENSIONS={'png','jpg'}
JSON_DATA=[]

app=Flask(__name__)
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
app.config['JSON_UPLOAD_FOLDER']=JSON_UPLOAD_FOLDER
app.config['CURRENT_IMAGE']=CURRENT_IMAGE
app.config['CURRENT_IMAGE_DATA']=CURRENT_IMAGE_DATA
app.config['JSON_DATA']=JSON_DATA

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

def makeGreyscale(img):
    img=ImageOps.grayscale(img)
    print(type(img))
    return img

def customResize(img,newWidth,size):

    oldWidth=size[0]
    oldHeight=size[1]
    newHeight=round(oldHeight*(newWidth/oldWidth))
    img=img.resize([newWidth,newHeight],resample=Image.BILINEAR)
    return img

@app.route('/editor',methods=['POST','GET'])
def runEditor():

    if os.path.exists('data.json'):
        try:
            with open('data.json') as datafile:
                app.config['JSON_DATA'] = json.load(datafile)
        except:
            with open('data.json','w') as datafile:
                json.dump(app.config['JSON_DATA'],datafile)

    filename=''
    errorMsg='No file chosen'

    imgConfig=request.form
    print(imgConfig)
    pixDeg=50
    greyscale=False
    doLibUpload=False

    if 'uploadToLib' in imgConfig and imgConfig['uploadToLib']=='True':
        doLibUpload=True

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

    script_dir= os.path.dirname(__file__) 
    rel_path= os.path.join(app.config['UPLOAD_FOLDER'],app.config['CURRENT_IMAGE'])
    abs_file_path= os.path.join(script_dir, rel_path)
    isolatedFilename=app.config['CURRENT_IMAGE'][:-4]
    abs_file_path_edited=os.path.join(script_dir,isolatedFilename+'_pixelated.png')

    try:
        if os.path.isfile(app.config['UPLOAD_FOLDER']+app.config['CURRENT_IMAGE']):

            #DO IMAGE PROCESSING IF IMAGE EXISTS
            img=Image.open(abs_file_path,'r')
            img=pixelate(img=img,size=img.size,pxFactor=int(imgConfig['pixDeg']))
            img=customResize(img=img,size=img.size,newWidth=int(imgConfig['newWidth']))
            pixDeg=int(imgConfig['pixDeg'])
            if 'greyscale' in imgConfig:
                img=makeGreyscale(img)
                greyscale=True
            if os.path.exists(abs_file_path_edited):
                os.remove(abs_file_path_edited)
            img.save(app.config['UPLOAD_FOLDER']+isolatedFilename+'_pixelated'+'.png')
            
            app.config['CURRENT_IMAGE_DATA']['width']=(img.size)[0]
            app.config['CURRENT_IMAGE_DATA']['height']=(img.size)[1]

            if doLibUpload:
                listImg=json.dumps(np.array(img).tolist())
                imgName=isolatedFilename+'_pixelated'+'.png'
                dataPiece={'name':imgName,'data':listImg}
                app.config['JSON_DATA'].append(dataPiece)
                with open('data.json','w') as datafile:
                    json.dump(app.config['JSON_DATA'],datafile)
        
        else:
            app.config['CURRENT_IMAGE']=''
    
    except:
        pass

    if not doLibUpload:
        return render_template('editor.html',
        filename=isolatedFilename+'_pixelated'+'.png',
        width=app.config['CURRENT_IMAGE_DATA']['width'],
        height=app.config['CURRENT_IMAGE_DATA']['height'],
        greyscale=greyscale,
        pixDeg=pixDeg,
        errorMsg=errorMsg
        )
    else:
        print('Redirecting')
        return redirect('library')


@app.route('/library')
def imageLib():
    with open('data.json') as datafile:
        imgData=json.load(datafile)
    resultImgData=[]
    for file in imgData:
        img=file['data']
        filename=file['name']
        img=Image.fromarray(np.array(json.loads(img), dtype='uint8'))
        img.save(app.config['JSON_UPLOAD_FOLDER']+filename)
        
        rel_path= os.path.join(app.config['JSON_UPLOAD_FOLDER'],filename)
        resultImgData.append({'name':filename,'imgPath':rel_path})

    return render_template('library.html',imgData=resultImgData)

@app.route('/library/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    script_dir= os.path.dirname(__file__) 
    jsonUploads = os.path.join(app.config['JSON_UPLOAD_FOLDER'],filename)
    return send_file(jsonUploads, as_attachment=True)

app.run(host='0.0.0.0', port=8080, debug=True)