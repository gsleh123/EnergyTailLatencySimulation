#!flask/bin/python
from flask import Flask, make_response, send_from_directory, request
import numpy as np
import random
import json
import sys

app = Flask(__name__)
latest_hosts = []

@app.route('/js/<path:path>')
def JS(path):
    return send_from_directory('js', path)

@app.route('/css/<path:path>')
def CSS(path):
    return send_from_directory('css', path)

@app.route('/')
def index():
    return make_response(open('index.html').read())

@app.route('/api/<int:id>')
def api(id):
    global latest_hosts

    j = {}
    if len(latest_hosts) == 0:
        j['packet_queue_size'] = 0
    else:
        j['packet_queue_size'] = latest_hosts['val']
    #sys.stderr.write("%i" % Host.hosts[0].packet_queue.qsize())
    return json.dumps(j)
        
@app.route('/update/hosts/', methods=['POST'])
def UpdateHosts(resp):
    global latest_hosts
    
    latest_hosts = request.get_json(force=True, silent=True)
    print latest_hosts
    return resp

@app.route('/shutdown')
def shutdown():
    shutdown_server()
    return 'Server Shutting Down'

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

def StartWebStreamer():
    app.run(debug = True, port=5656)

if __name__ == '__main__':
    StartWebStreamer()
