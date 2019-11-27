from flask import Flask, render_template, request, redirect, url_for
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
    if request.method == 'GET':
        path = '/' if path == '' else f'/{path}/'
        prev = '/'.join(path.split('/')[:-2])
        d, f = Files(db_name).items_in_folder(path)

        return render_template('dirs.html', dirs=d, files=f, path=path, prev=prev)
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
    files.drop_table()

    return redirect(url_for('dirs'))



app.run(debug=True)
