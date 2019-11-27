import sys
from flask import Flask, request, send_file

app = Flask(__name__)
ROOTDIR = 'FILE/'


@app.route('/<path:path>', methods=['GET', 'POST'])
def upload_file(path):
    if request.method == 'GET':
        return send_file(ROOTDIR + path)


if __name__ == '__main__':
    if sys.argv[1:]:
        port = int(sys.argv[1])
    else:
        port = 8000

    app.run(debug=True, port=port)
