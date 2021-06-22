from flask import Flask
from flask import render_template, request, json
from werkzeug.exceptions import HTTPException

app=Flask(__name__)

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

@app.route('/editor')
def openEditor():
    return render_template('editor.html')

@app.route('/library')
def imageLib():
    return render_template('library.html')

app.run(host='0.0.0.0', port=8080, debug=True)

#TODO: 
#Add base footer
#Chage icon: Transparent O center
#Test image form