from flask import Flask, jsonify
from flask_cors import CORS
import random
import math
import time

app = Flask(__name__)
CORS(app) 

@app.route('/api/cpu/count')
def cpu_count():
    return jsonify({"value": random.randint(4, 32)})

@app.route('/api/cpu/util')
def cpu_util():
    x = time.time() /7
    value = (math.sin(x) +1) /2 *100
    return jsonify({"value": round(value, 1)})

@app.route('/api/cpu/core_util')
def cpu_core_util():
    core_count =12
    cores = []
    for i in range(core_count):
        usage = round(random.uniform(0, 100), 1)  #0.0 ~100.0, 소수점 1자리
        cores.append({'id': i, 'usage': usage})
    return jsonify({"cores": cores})

@app.route('/api/gpu/count')
def gpu_count():
    return jsonify({"value": random.randint(0, 8)})

@app.route('/api/gpu/util')
def gpu_util():
    return jsonify({"value": random.randint(0, 100)})

@app.route('/api/gpu/util_detail')
def gpu_util_detail():
    gpu_count =6
    gpus = []
    now = time.time()
    for i in range(gpu_count):
        # 위상(phase)은 코어마다 다르게: 0, 60°, 120°, ...,300°
        phase = i * (2 * math.pi / gpu_count)
        # 주기는 예시로 15초, 진폭/offset 조절해 사용률 0~100 사이
        value = (math.sin(now /7 + phase) +1) /2 *100
        gpus.append({'id': i, 'usage': round(value, 1)})
    return jsonify({"gpus": gpus})

@app.route('/api/mem/total')
def mem_total():
    return jsonify({"value": random.choice([64, 128, 256, 512])})

@app.route('/api/mem/util')
def mem_util():
    return jsonify({"value": random.randint(0, 100)})

@app.route('/api/system/idle_time')
def idle_time():
    return jsonify({"value": random.randint(0, 10000)})

@app.route('/api/system/uptime')
def up_time():
    return jsonify({"value": random.randint(0, 10000)})

if __name__ == '__main__':
    app.run('0.0.0.0', port=8000, debug=True)