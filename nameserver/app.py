from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from db import Files
from node_manager import NodeManager
import requests as r

app = Flask(__name__)
app.jinja_env.globals.update(zip=zip)
db_name = 'db'
files = Files(db_name)
app.secret_key = 'hello'
node_man = NodeManager()
timer = node_man.heartbeat_ask()


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
    path = '/' if path == '' else f'/{path}'
    prev = '/'.join(path.split('/')[:-2])
    prev = '/' if prev == '' else prev + '/'

    if request.method == 'GET':
        d, f = files.items_in_folder(path)
        if '' in f:
            f.remove('')

        paths = [f'{path}/{el}' for el in f] if path != '/' else [f'/{el}' for el in f]
        infos = files.get_infos(paths)
        return render_template('dirs.html', dirs=d, files=f, path=path, prev=prev, infos=infos)
    else:
        location = request.form['path']
        d_name = request.form['dir_name']
        d_path = f'{location}{"" if location != "/" else ""}{d_name}/'
        if request.form['method'] == 'PUT':
            if not files.exists(d_path):
                files.add(d_path)
                node_man.add_dir(d_path)
            else:
                flash('Directory already exists')
        elif request.form['method'] == 'DELETE':
            if files.exists(d_path):
                files.del_file(d_path)
                node_man.del_dir(d_path)
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
        send_node = node_man.get_storages()[0]
        return redirect("http://"+send_node+"/files/"+path)
    elif request.method == 'POST':
        print(request.form['path'])
        location = request.form['path']
        f_name = request.form['file_name']
        f_path = f'{location}{f_name}'

        if request.form['method'] == 'UPLOAD':
            return ','.join(node_man.get_storages())
        elif request.form['method'] == 'CREATE':
            if not files.exists(f_path):
                files.add(f_path)
                if request.form['not_create'] == 'false':
                    node_man.create_empty_file(f_path)
        elif request.form['method'] == 'DELETE':
            if files.exists(f_path):
                files.del_file(f_path)
                node_man.del_dir(f_path)
            else:
                flash('File does not exist')
        else:
            flash('Something went wrong')
    return redirect(url_for('dirs'))


@app.route('/copy', methods=['POST'])
def copy():
    '''
    Copy source file to the target directory
    '''
    if request.method == 'POST':
        path = request.form['path'].strip().lstrip()
        source = request.form['source'].strip().lstrip()
        target = request.form['target'].strip().lstrip()

        if not target.endswith('/'):
            target = target + '/'

        files.copy_file(source, target, path)
        node_man.copy_dir(path + source, target)

        if path == '/':
            return redirect('/dirs/')
        else:
            return redirect('/dirs' + path)




    return redirect(url_for('dirs'))

@app.route('/move', methods=['POST'])
def move():
    '''
    Move source file to the target directory
    '''
    if request.method == 'POST':
        path = request.form['path'].strip().lstrip()
        source = request.form['source'].strip().lstrip()
        target = request.form['target'].strip().lstrip()

        if not target.endswith('/'):
            target = target + '/'

        # Move file in both nameserver and nodes
        files.move_file(source, target, path)
        node_man.move_dir(path + source, target)

        # Redirect
        if path == '/':
            return redirect('/dirs/')
        else:
            return redirect('/dirs' + path)

    return redirect(url_for('dirs'))

@app.route('/init', methods=['GET'])
def init():
    '''
    Send command to delete files to storage nodes
    Return index page
    '''
    files.drop_table()
    flash('Initialized correctly')

    # send init command to storage servers
    node_man.del_dir('/*')

    return redirect(url_for('dirs'))


@app.route('/get/storages', methods=['GET'])
def storages():
    storages = node_man.get_storages().copy()
    node_man.add_node(request.remote_addr)
    return ','.join(storages)


app.run(host='0.0.0.0', debug=True)
timer.cancel()
