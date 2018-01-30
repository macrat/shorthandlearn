import json
import random

import flask


app = flask.Flask(__name__)


def db_store(data):
    try:
        with open('data.json') as f:
            db = json.load(f)
    except IOError:
        db = {}

    if data['text'] not in db:
        db[data['text']] = []

    db[data['text']].append(data['path'])

    with open('data.json', 'w') as f:
        json.dump(db, f)


def db_getone(text):
    try:
        with open('data.json') as f:
            db = json.load(f)
    except:
        return None

    if text in db:
        return random.choice(db[text])
    else:
        return None


@app.route('/')
def index():
    with open('index.html') as f:
        return f.read()


@app.route('/app.js')
def script():
    with open('app.js') as f:
        return flask.Response(f.read(), mimetype='application/javascript')


@app.route('/bg.png')
def bgimage():
    with open('bg.png', 'rb') as f:
        return flask.Response(f.read(), mimetype='image/png')


@app.route('/store', methods=['POST'])
def store():
    db_store(flask.request.json)
    return '', 201


@app.route('/example')
def example():
    data = db_getone(flask.request.args['text']) 
    if data is not None:
        return flask.Response(
            json.dumps(data),
            mimetype='application/json',
        )
    else:
        return '[]', 404


if __name__ == '__main__':
    app.run(debug=True)
