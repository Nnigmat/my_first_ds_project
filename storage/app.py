import sys
import os
import threading
import requests
import time
from flask import Flask, request, send_file, abort
from multiprocessing import Pool

app = Flask(__name__)
NAMESERVER = '127.0.0.1:4000'
PORT = '8081'
ROOTDIR = 'file/'
NODES = ['127.0.0.1']
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
        init()
    else:
        pass
        # Somehow save


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


@app.route('/ask/new', methods=['GET'])
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


def heartbeat_ask(repeatTime=15.0):
    """
    Every repeatTime seconds check that node is reachable
    """
    timer = threading.Timer(repeatTime, heartbeat_ask)
    timer.start()
    for node in NODES:
        url = createURL(node, PORT)
        try:
            requests.get(url=url)
        except requests.exceptions.ConnectionError:
            if node in FAILED_NODES:
                NODES.remove(node)
                FAILED_NODES.remove(node)
                print(node, "removed")
            else:
                FAILED_NODES.append(node)
                print(node, "failed")
        else:
            if node in FAILED_NODES:
                FAILED_NODES.remove(node)
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
        port = int(sys.argv[1])
    else:
        port = 8080

    if not os.path.exists(ROOTDIR):
        os.makedirs(ROOTDIR)

    init()
    heartbeat = heartbeat_ask()
    app.run(port=port)
    heartbeat.cancel()
