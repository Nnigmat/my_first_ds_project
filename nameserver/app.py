from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from db import Files
import requests as r

app = Flask(__name__)
db_name = 'db'
files = Files(db_name)
app.secret_key = 'hello'

@app.route('/')
def index():
    return redirect(url_for('dirs'))


@app.route('/dirs/', defaults={'path': ''}, methods=['POST', 'GET'])
@app.route('/dirs/<path:path>', methods=['POST', 'GET'])
def dirs(path):
    '''
    GET:
        If path is empty => return file structure at root
        If the path is valid => return file structure in a given directory
        Otherwise => Error

    POST:
        Create new directory in the given path
        Delete directory
    '''
    path = '/' if path == '' else f'/{path}/'
    prev = '/'.join(path.split('/')[:-2])
    prev = '/' if prev == '' else prev

    if request.method == 'GET':
        d, f = files.items_in_folder(path)
        print(d, f, path)
        return render_template('dirs.html', dirs=d, files=f, path=path, prev=prev)
    else:
        location = request.form['path']
        d_name = request.form['dir_name']
        d_path = f'{location}{"/" if location != "/" else ""}{d_name}/'
        print(location, d_name, d_path)
    
        if request.form['method'] == 'PUT':
            if not files.exists(d_path):
                files.add(d_path)
                # send created folder to server
            else:
                flash('Directory already exists')
        elif request.form['method'] == 'DELETE':
            if files.exists(d_path):
                files.del_file(d_path)
                # send deleted folder to server
            else:
                flash("Directory doesn't exists")
        return redirect(f'/dirs{location}')


@app.route('/file/', methods=['GET', 'POST'], defaults={'path': ''})
@app.route('/file/<path:path>', methods=['GET', 'POST'])
def file(path):
    '''
    GET:
        Download file at given path

    POST:
        Upload file to given path or create new empty one
        Delete file
    '''
    
    if request.method == 'GET':
        # Should return list of availagle ip addresses to user
        return jsonify(ips=['127.0.0.1'], ports=['5000'])
    elif request.method == 'POST':
        location = request.form['path']
        f_name = request.form['file_name']
        f_path = f'{location}{f_name}/'

        if request.form['method'] == 'UPLOAD':
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            f = request.files['file']
            if f.filename == '':
                flash('No selected file')
                return rederect(requeest.url)

            print(f, dir(f))
            # Need to implement sending to cluster
            r.post('url' ,f.read())
        elif request.form['method'] == 'CREATE':
            if not files.exists(f_path):
                files.add(f_path)
        elif request.form['method'] == 'DELETE':
            if files.exists(f_path):
                files.del_file(f_path)
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
    files.drop_table()
    flash('Initialized correctly')

    return redirect(url_for('dirs'))


app.run(debug=True)
