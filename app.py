import os
from flask import Flask,request
from flask import Flask,render_template
import requests
import json
import datetime
import collections
from flask import jsonify
from models.models import *
from flask.ext.mongoengine import MongoEngine
from flask.ext.mongoengine.wtf import model_form

app = Flask(__name__)
app.config.from_object('config')
mongoDb = MongoEngine(app)
mongoDb.connect()


def convert(data):
    if isinstance(data, basestring):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(convert, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convert, data))
    else:
        return data

@app.route('/')
@app.route('/index')
def index():
    log = json.loads((get_gateway_status()).data)
    log = json.loads(log['data'])
    logs = []
    for data in log:
        # data['timestamp'] = datetime.datetime.fromtimestamp(data['timestamp']).strftime('%d-%m-%Y %H:%M:%S')
        # print data['timestamp']
        logs.append(data)
    return render_template('index.html',log=logs)

@app.route('/lrs/api/v1.0/gateway/status', methods=['GET'])
def get_gateway_status():    
    status = GatewayStatus.objects.all().order_by('-timestamp')[:6]
    return jsonify(data=status.to_json())


@app.route('/lrs/api/v1.0/gateway/status', methods=['POST'])
def set_gateway_status():

    vm =  request.json['memory']['virtual_memory']
    sm =  request.json['memory']['swap_memory']
    ni =  request.json['network']['network_info']
    ci =  request.json['cpu']['cpu_info']
    virtual_memory = VirtualMemory(**vm)
    swap_memory = SwapMemory(**sm)
    network_info = NetworkInfo(**ni)
    cpu_info = CpuInfo(**ci)
    memory = Memory(virtual_memory=virtual_memory,swap_memory=swap_memory)
    network = Network(network_info=network_info)
    cpu = Cpu(cpu_info=cpu_info)
    gs = GatewayStatus(memory=memory,network=network,cpu=cpu,timestamp=request.json['timestamp'])
    gs.save() 

    return jsonify(data=gs.to_json())    

# launch
if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)