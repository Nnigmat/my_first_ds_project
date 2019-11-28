from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from db import Files

app = Flask(__name__)
db_name = 'db'
files = Files(db_name)
app.secret_key = 'hello'

@app.route('/')
def index():
    return render_template('index.html')


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

        return render_template('dirs.html', dirs=d, files=f, path=path, prev=prev)
    else:
        d_name = request.form['dir_name']
        location = request.form['path']
        print(location)
        d_path = f'{location}{d_name}/'
        print(d_path)
    
        if request.form['method'] == 'PUT':
            if not files.exists(d_path):
                files.add(d_path)
        else:
            if files.exists(d_path):
                files.del_file(d_path)
        return redirect(f'/dirs{d_path}')


@app.route('/file/', methods=['GET', 'POST'], defaults={'path': ''})
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
        # Should return list of availagle ip addresses to user
        return jsonify(ips=['127.0.0.1'], ports=['5000'])
    elif request.method == 'POST':
        '''
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        f = request.files['file']
        if f.filename == '':
            flash('No selected file')
            return rederect(requeest.url)

        if f and allowed_file(f.filename):
            pass
        '''
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
    files.drop_table()
    flash('Initialized correctly')

    return redirect(url_for('dirs'))



app.run(debug=True)
