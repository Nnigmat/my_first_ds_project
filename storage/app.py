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
NAMESERVER = '127.0.0.1:4000'
PORT = '8080'
ROOTDIR = 'file/'
NODES = []
FAILED_NODES = []
app.config['UPLOAD_FOLDER'] = ROOTDIR


def init():
    """
    Ask nameserver for storage nodes until it answer
    """
    url = createURL(NAMESERVER, path="/get/storages")
    try:
        r = requests.get(url=url)
    except requests.exceptions.ConnectionError:
        time.sleep(10)
        return init()
    else:
        NODES = r.values["to"]

    for node in NODES:
        url = createURL(node, PORT, "/ask/files")
        try:
            r = requests.get(url=url)
        except requests.exceptions.ConnectionError:
            continue
        else:
            break

    for node in NODES:
        url = createURL(node, PORT, "/ask/new")
        try:
            r = requests.get(url=url)
        except requests.exceptions.ConnectionError:
            continue


@app.route('/file/<path:path>', methods=['GET', 'POST'])
def upload_file(path):
    """
    GET:
        Return file by path if exist else 418
    POST:
        Return 201 if file successful saved  else 400
    """
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
        for node in NODES:
            sync_file(filepath, node)
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
    return filepath, 201


@app.route('/delete/<path:path>', methods=['GET'])
def delete(path):
    """
    GET:
        Delete folder or file
    """
    filepath = os.path.join(ROOTDIR, path)
    if os.path.exists(filepath):
        if os.path.isfile(filepath):
            os.remove(filepath)
        else:
            shutil.rmtree(filepath)
    for node in NODES:
        sync_action(node, '/delete/' + path)
    return "Done", 201


@app.route('/move/<path:path>', methods=['GET'])
def move(path):
    moveFrom = os.path.join(ROOTDIR, path)
    moveTo = os.path.join(ROOTDIR, request.values["to"])
    if not os.path.exists(moveFrom):
        abort(400)
    shutil.move(moveFrom, moveTo)
    for node in NODES:
        sync_action(node, '/move/' + path, {'to': request.values["to"]})
    return "Done", 201


@app.route('/copy/<path:path>', methods=['GET'])
def copy(path):
    copyFrom = os.path.join(ROOTDIR, path)
    copyTo = os.path.join(ROOTDIR, request.values["to"])
    print(copyTo)
    if not os.path.exists(copyFrom):
        abort(400)
    if os.path.isfile(copyFrom):
        shutil.copy(copyFrom, copyTo)
    else:
        dir_util.copy_tree(copyFrom, copyTo)

    for node in NODES:
        sync_action(node, '/copy/' + path, {'to': request.values["to"]})
    return "Done", 201


@app.route('/ask/new', methods=['GET'])
def add_node():
    """
    GET:
        Send all files to client
    """
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
    # for file in files:
    #     sync_file(file, storageAddr)
    # print(files)
    with Pool(processes=8) as pool:
        pool.starmap(sync_file, map(lambda x: (x, storageAddr), files))
    return 'Done', 200


def sync_file(filepath, addr):
    """
    Send file to addr
    """
    url = createURL(addr, PORT, filepath)
    file = {'file': open(filepath, 'rb')}
    try:
        requests.post(url, files=file)
    except requests.exceptions.ConnectionError:
        print(addr, "is failed")


def sync_action(addr, action, params={}):
    """
    Go to some storage url which do action
    Action is path
    """
    url = createURL(addr, PORT, action)
    try:
        requests.get(url, params=params)
    except requests.exceptions.ConnectionError:
        print(addr, "is failed")


def heartbeat_ask(repeatTime=15.0):
    """
    Every repeatTime seconds check that node is reachable
    """
    timer = threading.Timer(repeatTime, heartbeat_ask)
    timer.start()
    for node in NODES + FAILED_NODES:
        url = createURL(node, PORT)
        try:
            requests.get(url=url)
        except requests.exceptions.ConnectionError:
            if node in FAILED_NODES:
                FAILED_NODES.remove(node)
                print(node, "removed")
            else:
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

    # init()
    heartbeat = heartbeat_ask()
    app.run(host='0.0.0.0', port=PORT)
    heartbeat.cancel()
