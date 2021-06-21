from flask import Flask
from flask import render_template, request, json
from werkzeug.exceptions import HTTPException

app=Flask(__name__)

#Run env\Scripts\activate to activate venv
#TASK: Add error handlers

@app.route('/')
def root():
    return render_template('index.html')

@app.errorhandler(HTTPException)
def handle_exception(e):
    error = {'code':e.code,'name':e.name,'description':e.description}
    return render_template('error.html', error=error)

app.run(host='0.0.0.0', port=8080, debug=True)