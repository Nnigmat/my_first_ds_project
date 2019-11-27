from flask import Flask, render_template, request, redirect
from db import Files

app = Flask(__name__)
db_name = 'db'

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/dirs/', defaults={'path': ''}, methods=['POST', 'GET'])
@app.route('/dirs/<path:path>', methods=['POST', 'GET', 'DELETE'])
def dirs(path):
    '''
    GET:
        If path is empty => return file structure at root
        If the path is valid => return file structure in a given directory
        Otherwise => Error

    POST:
        Create new directory in the given path

    DELETE:
        Delete directory
    '''
    if path == '':
        path = '/'
    else:
        path = f'/{path}/'
    
    files = Files(db_name)
    d, f = files.items_in_folder(path)
    print(path, d, f)

    if request.method == 'GET':
        return render_template('dirs.html', dirs=d, files=f, path=path)
    elif request.method == 'POST':
        pass
    elif request.method == 'DELETE':
        pass

    return path


@app.route('/file/<path:path>', methods=['GET', 'POST', 'DELETE'])
def file(path):
    '''
    GET:
        Download file at given path

    POST:
        Upload file to given path or create new empty one

    DELETE:
        Delete file at given path
    '''

    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        pass
    elif request.method == 'DELETE':
        pass

    return path


@app.route('/info/<path:path>')
def info(path):
    '''
    Return info about file
    '''
    return path


@app.route('/copy', methods=['POST'])
def copy(path):
    '''
    Copy source file to the target directory
    '''
    if request.method == 'POST':
        source, target = request.form['source'], request.form['target']


@app.route('/move', methods=['POST'])
def move():
    '''
    Move source file to the target directory
    '''
    if request.method == 'POST':
        source, target = request.form['source'], request.form['target']


@app.route('/init', methods=['POST'])
def init():
    '''
    Send command to delete files to storage nodes
    Return index page
    '''
    files = Files(db_name)

    return redirect(url_for('dirs'))



app.run(debug=True)
