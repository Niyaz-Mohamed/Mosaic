#Import packages
from flask import Flask
from flask import render_template, request, flash, request, redirect, send_file
from werkzeug.exceptions import HTTPException
from werkzeug.utils import secure_filename

from PIL import Image, ImageOps
import os,json
import numpy as np

#Activate venv
dir_path=os.path.dirname(os.path.realpath(__file__))

#Define global variables stores internally within the app itslef
UPLOAD_FOLDER='./static/uploads/'
JSON_UPLOAD_FOLDER='./static/json/'
CURRENT_IMAGE=''
CURRENT_IMAGE_DATA={'width':0,'height':0}
JSON_DATA=[]

app=Flask(__name__)
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
app.config['JSON_UPLOAD_FOLDER']=JSON_UPLOAD_FOLDER
app.config['CURRENT_IMAGE']=CURRENT_IMAGE
app.config['CURRENT_IMAGE_DATA']=CURRENT_IMAGE_DATA
app.config['JSON_DATA']=JSON_DATA

#Add a list to the json file if it exists
if os.path.exists('data.json'):
    try:
        with open('data.json') as datafile:
            app.config['JSON_DATA'] = json.load(datafile)
    except:
        with open('data.json','w') as datafile:
            json.dump(app.config['JSON_DATA'],datafile)

def allowedFile(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png','jpg'}

#General Error Handler
@app.errorhandler(HTTPException)
def handle_exception(e):
    error = {'code':e.code,'name':e.name,'description':e.description}
    return render_template('error.html', error=error)

#Error route for checking of the error page
@app.route('/error')
def showError():
    return render_template('error.html', error={'code':': )','name':'no error here','description':'don\'t go peeking at my code'})

#Root route redirects to home
@app.route('/')
def baseRedirect():
    return redirect('home')

#Home route
@app.route('/home')
def root():

    title_desc="""Mosiac allows you to take a high-definition image and convert it to pixel art.\n 
    It provides features to freely control the degree of pixelization, make an image greyscale, 
    or change the palette used by the image."""

    return render_template('index.html',title_desc=title_desc)

#Route to check the base html template
@app.route('/base')
def loadBase():
    return render_template('base.html',noLoadFooter=True)

#Image pixelation function
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

#Image greyscale function
def makeGreyscale(img):
    img=ImageOps.grayscale(img)
    return img

#Image resize (keeping ratio) function
def customResize(img,newWidth,size):

    oldWidth=size[0]
    oldHeight=size[1]
    newHeight=round(oldHeight*(newWidth/oldWidth))
    img=img.resize([newWidth,newHeight],resample=Image.BILINEAR)
    return img

#Main editor route
@app.route('/editor',methods=['POST','GET'])
def runEditor():

    #Check json again
    if os.path.exists('data.json'):
        try:
            with open('data.json') as datafile:
                app.config['JSON_DATA'] = json.load(datafile)
        except:
            with open('data.json','w') as datafile:
                json.dump(app.config['JSON_DATA'],datafile)

    #Define variables to be used in this function 
    imgConfig=request.form
    filename=''
    errorMsg='No file chosen'
    pixDeg=50
    greyscale=False
    doLibUpload=False

    #Prepare to send the image to the library if needed
    if 'uploadToLib' in imgConfig and imgConfig['uploadToLib']=='True':
        doLibUpload=True

    #Handle file upload
    if request.method == 'POST' :
        
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
                
            if file and allowedFile(file.filename):
                filename=secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
                app.config['CURRENT_IMAGE']=filename

        except:
            errorMsg='Error: Please try again'

    #Define some important file paths
    script_dir= os.path.dirname(__file__) 
    rel_path= os.path.join(app.config['UPLOAD_FOLDER'],app.config['CURRENT_IMAGE'])
    abs_file_path= os.path.join(script_dir, rel_path)
    isolatedFilename=(app.config['CURRENT_IMAGE'].split('.'))[0]
    abs_file_path_edited=os.path.join(script_dir,isolatedFilename+'_pixelated.png')

    if os.path.isfile(app.config['UPLOAD_FOLDER']+app.config['CURRENT_IMAGE']):

        #Do image processing if the image exists
        img=Image.open(abs_file_path,'r')
        img=pixelate(img=img,size=img.size,pxFactor=int(imgConfig['pixDeg']))
        img=customResize(img=img,size=img.size,newWidth=int(imgConfig['newWidth']))
        pixDeg=int(imgConfig['pixDeg'])
        if 'greyscale' in imgConfig:
            img=makeGreyscale(img)
            greyscale=True

        #Replace existing pixelated file with newly made file
        if os.path.exists(abs_file_path_edited):
            os.remove(abs_file_path_edited)
        img.save(app.config['UPLOAD_FOLDER']+isolatedFilename+'_pixelated'+'.png')
        
        #Change image data
        app.config['CURRENT_IMAGE_DATA']['width']=(img.size)[0]
        app.config['CURRENT_IMAGE_DATA']['height']=(img.size)[1]

        #Dump pixel list of the image into the json file
        if doLibUpload:
            listImg=json.dumps(np.array(img).tolist())
            imgName=isolatedFilename+'_pixelated'+'.png'
            fileNameList=[]

            #Change filename to ensure no file duplicates in the library 
            with open('data.json') as datafile:
                data=json.load(datafile)
                for file in data:
                    fileNameList.append(file['name'])
            if imgName in fileNameList:
                prefix=0
                while imgName in fileNameList:
                    prefix+=1
                    imgName=isolatedFilename+'_pixelated'+'('+str(prefix)+')'+'.png'
                    if imgName in fileNameList:
                        continue
                    else:
                        break
            
            #Add the data to the json file
            dataPiece={'name':imgName,'data':listImg}
            app.config['JSON_DATA'].append(dataPiece)
            with open('data.json','w') as datafile:
                json.dump(app.config['JSON_DATA'],datafile)

    #Render editor if image upload to library is not needed
    if not doLibUpload:

        return render_template('editor.html',
        filename=isolatedFilename+'_pixelated'+'.png',
        width=app.config['CURRENT_IMAGE_DATA']['width'],
        height=app.config['CURRENT_IMAGE_DATA']['height'],
        greyscale=greyscale,
        pixDeg=pixDeg,
        errorMsg=errorMsg
        )

    #Redirect to the library 
    else:
        app.config['CURRENT_IMAGE']=''
        return redirect('library')


@app.route('/library')
def imageLib():
    with open('data.json') as datafile:
        imgData=json.load(datafile)
        imgData.reverse()
    resultImgData=[]

    #Convert data in json file to a dictionary to pass into the library template
    for file in imgData:
        img=file['data']
        filename=file['name']
        img=Image.fromarray(np.array(json.loads(img), dtype='uint8'))
        img.save(app.config['JSON_UPLOAD_FOLDER']+filename)
        
        rel_path= os.path.join(app.config['JSON_UPLOAD_FOLDER'],filename)
        resultImgData.append({'name':filename,'imgPath':rel_path})

    return render_template('library.html',imgData=resultImgData)

#Generate file download links
@app.route('/library/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    jsonUploads = os.path.join(app.config['JSON_UPLOAD_FOLDER'],filename)
    return send_file(jsonUploads, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)