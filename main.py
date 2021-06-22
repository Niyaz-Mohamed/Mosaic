from flask import Flask
from flask import render_template, request, json
from werkzeug.exceptions import HTTPException

app=Flask(__name__)

#Run env\Scripts\activate to activate venv
#TASK: Add error handlers

@app.route('/')
def root():
    with open('./static/assets/title_desc.txt', 'r') as file:
        title_desc = file.read().replace('\n', '')
    return render_template('index.html',title_desc=title_desc)

@app.errorhandler(HTTPException)
def handle_exception(e):
    error = {'code':e.code,'name':e.name,'description':e.description}
    return render_template('error.html', error=error)

app.run(host='0.0.0.0', port=8080, debug=True)