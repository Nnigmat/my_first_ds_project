import sys
import os
from flask import Flask, request, send_file, abort

app = Flask(__name__)
ROOTDIR = 'FILE/'
app.config['UPLOAD_FOLDER'] = ROOTDIR


@app.route('/<path:path>', methods=['GET', 'POST'])
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


if __name__ == '__main__':
    if sys.argv[1:]:
        port = int(sys.argv[1])
    else:
        port = 8080

    app.run(debug=True, port=port)
