# Run with "python client.py"
from bottle import get, run, static_file, route, template

@route('/hello/<name>')
def hello(name="Stranger"):
  return template('Hello {{name}}, how are you', name=name)

@get('/')
def index():
    return static_file('index.html', root=".")

run(host='localhost', port=5000)
