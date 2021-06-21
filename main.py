from flask import Flask
from flask import render_template, request

app=Flask(__name__)

#Run env\Scripts\activate to activate venv
#TASK: Add error handlers

@app.route('/<name>')
def general(name):
    return "<h1>"+str(name)+"</h1>"

@app.route('/')
def root():
    return "<h1>Welcome to my Website!<h1>"

app.run(host='0.0.0.0', port=8080, debug=True)