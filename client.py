# Run with "python client.py"
from bottle import get, run, static_file, route, template 

import os
import sys

dirname = os.path.dirname(sys.argv[0])
print(dirname)

# Static Routes
@get("/static/css/<filepath:re:.*\.css>")
def css(filepath):
    return static_file(filepath, root="static/css")


@get("/static/js/<filepath:re:.*\.js>")
def js(filepath):
    return static_file(filepath, root="static/js")

@get('/')
def index():
  return static_file('index.html', root=".")

@get('/main')
def main():
  return static_file("main.html", root=".")



run(reloader=True, host='localhost', port=5000)
