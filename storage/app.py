import sys
import os
import threading
import requests
import time
import shutil
import distutils.dir_util as dir_util
from flask import Flask, request, send_file, abort
from multiprocessing import Pool

app = Flask(__name__)
NAMESERVER = 'http://3.134.97.176:5000'
# NAMESERVER = 'http://127.0.0.1:5000'
PORT = '8080'
ROOTDIR = 'file/'
NODES = []
FAILED_NODES = []
app.config['UPLOAD_FOLDER'] = ROOTDIR


def init():
    """
    Ask nameserver for storage nodes until it answer
    """
    global NODES
    url = NAMESERVER + "/get/storages"
    try:
        r = requests.get(url=url, timeout=0.1)
    except requests.exceptions.RequestException:
        print("NAMESERVER NOT ANSWER")
        time.sleep(10)
        return init()
    else:
        addrsText = r.text
        if len(addrsText) != 0:
            NODES = addrsText.split(',')

    print(NODES)
    nodes = NODES.copy()
    for node in nodes:
        url = createURL(node, PORT, "ask/files")
        try:
            r = requests.get(url=url, timeout=0.1)
        except requests.exceptions.RequestException:
            continue
        else:
            break

    for node in nodes:
        url = createURL(node, PORT, "ask/new")
        try:
            r = requests.get(url=url, timeout=0.1)
        except requests.exceptions.RequestException:
            continue


@app.route('/file/<path:path>', methods=['GET', 'POST'])
def upload_file(path):
    """
    GET:
        Return file by path if exist else 418
    POST:
        Return 201 if file successful saved  else 400
    """
    path = path[len('dirs/'):] if path.startswith('dirs/') else path
    filepath = os.path.join(ROOTDIR, path)
    if request.method == 'GET':
        if os.path.exists(filepath) and os.path.isfile(filepath):
            return send_file(filepath)
        abort(418)
    else:
        if 'file' not in request.files:
            abort(400)
        file = request.files['file']
        file.save(filepath)

        for node in NODES.copy():
            sync_file(filepath, node)
        return filepath, 201


@app.route('/sync/<path:path>', methods=['POST'])
def get_storage_file(path):
    filepath = path
    if 'file' not in request.files:
        abort(400)
    file = request.files['file']
    if not os.path.exists(os.path.dirname(filepath)):
        os.makedirs(os.path.dirname(filepath))
    file.save(filepath)
    return filepath, 201


@app.route('/create_file/<path:path>', methods=['GET'])
def empty_file(path):
    filepath = os.path.join(ROOTDIR, path)
    open(filepath, 'a').close()
    if request.args.get('sync'):
        return filepath, 201

    for node in NODES.copy():
        sync_action(node, 'create_file/' + path)

    return filepath, 201


@app.route('/dir/<path:path>', methods=['GET'])
def create_folder(path):
    """
    GET:
        Create folder
    """
    filepath = os.path.join(ROOTDIR, path)
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    if request.args.get('sync'):
        return filepath, 201

    for node in NODES.copy():
        sync_action(node, 'dir/' + path)

    return filepath, 201


@app.route('/delete/<path:path>', methods=['GET'])
def delete(path):
    """
    GET:
        Delete folder or file
    """
    filepath = os.path.join(ROOTDIR, path)
    if path == '*':
        filepath = ROOTDIR
    if os.path.exists(filepath):
        if os.path.isfile(filepath):
            os.remove(filepath)
        else:
            shutil.rmtree(filepath)

    if not os.path.exists(ROOTDIR):
        os.makedirs(ROOTDIR)

    if request.args.get('sync'):
        return "Done", 201

    for node in NODES.copy():
        sync_action(node, 'delete/' + path)

    return "Done", 201


@app.route('/move/<path:path>', methods=['GET'])
def move(path):
    moveFrom = os.path.join(ROOTDIR, path)
    moveTo = os.path.join(ROOTDIR, request.values["to"])
    if moveTo == '/':
        moveTo = ROOTDIR
    if not os.path.exists(moveFrom):
        abort(400)
    shutil.move(moveFrom, moveTo)

    if request.args.get('sync'):
        return "Done", 201

    for node in NODES.copy():
        sync_action(node, 'move/' + path, {'to': request.values["to"]})

    return "Done", 201


@app.route('/copy/<path:path>', methods=['GET'])
def copy(path):
    copyFrom = os.path.join(ROOTDIR, path)
    copyTo = os.path.join(ROOTDIR, request.values["to"])
    if copyTo == '/':
        copyTo = ROOTDIR
    if not os.path.exists(copyFrom):
        abort(400)
    if os.path.isfile(copyFrom):
        shutil.copy(copyFrom, copyTo)
    else:
        dir_util.copy_tree(copyFrom, copyTo)

    if request.args.get('sync'):
        return "Done", 201

    for node in NODES.copy():
        sync_action(node, 'copy/' + path, {'to': request.values["to"]})
    return "Done", 201


@app.route('/ask/new', methods=['GET'])
def add_node():
    storageAddr = request.remote_addr

    if storageAddr not in NODES:
        NODES.append(storageAddr)
    return 'Done', 200


@app.route('/ask/files', methods=['GET'])
def sync_files():
    """
    GET:
        Send all files to client
    """
    storageAddr = request.remote_addr
    files = getAllFilePaths()
    time.sleep(1)
    for file in files:
        sync_file(file, storageAddr)
    # with Pool(processes=8) as pool:
    #      pool.starmap(sync_file, map(lambda x: (x, storageAddr), files))
    return 'Done', 200


def sync_file(filepath, addr):
    """
    Send file to addr
    """
    print("sync with", addr)
    url = createURL(addr, PORT, 'sync/' + filepath)
    file = {'file': open(filepath, 'rb')}
    try:
        requests.post(url, files=file, timeout=0.5)
    except requests.exceptions.RequestException:
        print(addr, "is failed")


def sync_action(addr, action, params={}):
    """
    Go to some storage url which do action
    Action is path
    """
    url = createURL(addr, PORT, action)
    params['sync'] = True
    try:
        requests.get(url, params=params, timeout=0.5)
    except requests.exceptions.RequestException:
        print(addr, "is failed")
    return True


def heartbeat_ask(repeatTime=15.0):
    """
    Every repeatTime seconds check that node is reachable
    """
    timer = threading.Timer(repeatTime, heartbeat_ask)
    timer.start()
    for node in NODES + FAILED_NODES:
        url = createURL(node, PORT)
        try:
            requests.get(url=url, timeout=0.1)
        except requests.exceptions.RequestException:
            if node in FAILED_NODES:
                FAILED_NODES.remove(node)
                print(node, "removed")
            elif node in NODES:
                NODES.remove(node)
                FAILED_NODES.append(node)
                print(node, "failed")
        else:
            if node in FAILED_NODES:
                FAILED_NODES.remove(node)
                NODES.append(node)
    return timer


def createURL(addr='', port='', path=''):
    return "http://{}:{}/{}".format(addr, port, path)


def getAllFilePaths():
    filePaths = []
    for root, dirs, files in os.walk(ROOTDIR):
        for file in files:
            filePaths.append(os.path.join(root, file))
    return filePaths


if __name__ == '__main__':
    if sys.argv[1:]:
        NAMESERVER = sys.argv[1]

    if not os.path.exists(ROOTDIR):
        os.makedirs(ROOTDIR)
    else:
        shutil.rmtree(ROOTDIR)
        os.makedirs(ROOTDIR)

    init()
    heartbeat = heartbeat_ask()
    app.run(host='0.0.0.0', port=PORT)
    heartbeat.cancel()
