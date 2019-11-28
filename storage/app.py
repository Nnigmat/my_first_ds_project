import sys
import os
import threading
import requests
from flask import Flask, request, send_file, abort

app = Flask(__name__)
ROOTDIR = 'FILE/'
NODES = ['localhost:8080', 'localhost:8081']
FAILED_NODES = []
app.config['UPLOAD_FOLDER'] = ROOTDIR


@app.route('/file/<path:path>', methods=['GET', 'POST'])
def upload_file(path):
    filepath = os.path.join(ROOTDIR, path)
    if request.method == 'GET':
        if os.path.exists(filepath) and os.path.isfile(filepath):
            return send_file(ROOTDIR + path)
        abort(418)
    else:
        if 'file' not in request.files:
            abort(400)
        file = request.files['file']
        file.save(filepath)
        return filepath, 201


def heartbeat_ask():
    timer = threading.Timer(10.0, heartbeat_ask)
    timer.start()
    for node in NODES:
        url = "http://" + node + '/'
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


if __name__ == '__main__':
    if sys.argv[1:]:
        port = int(sys.argv[1])
    else:
        port = 8080

    heartbeat = heartbeat_ask()

    app.run(port=port)
    heartbeat.cancel()
