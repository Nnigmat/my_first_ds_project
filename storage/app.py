import sys
import os
import threading
import requests
from flask import Flask, request, send_file, abort

app = Flask(__name__)
PORT = '8081'
ROOTDIR = 'file/'
NODES = ['127.0.0.1']
FAILED_NODES = []
app.config['UPLOAD_FOLDER'] = ROOTDIR


@app.route('/file/<path:path>', methods=['GET', 'POST'])
def upload_file(path):
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
    storageAddr = request.remote_addr
    files = getAllFilePaths()
    for file in files:
        sync_file(file, storageAddr)
    return 'Done', 200


def sync_file(filepath, addr):
    url = createURL(addr, PORT, filepath)
    file = {'file': open(filepath, 'rb')}
    requests.post(url, files=file)


def heartbeat_ask():
    timer = threading.Timer(15.0, heartbeat_ask)
    timer.start()
    for node in NODES:
        url = createURL(node, PORT)
        try:
            r = requests.get(url=url)
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


def createURL(addr, port, filepath=''):
    return "http://{}:{}/{}".format(addr, port, filepath)


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

    heartbeat = heartbeat_ask()
    app.run(port=port)
    heartbeat.cancel()
