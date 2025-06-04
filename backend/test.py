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

@app.route('/api/gpu/temp_detail')
def gpu_temp_detail():
    gpu_count =6
    gpus = []
    for i in range(gpu_count):
        # 온도 30~80℃ 범위 랜덤값 (예시)
        temp = round(random.uniform(30, 200), 1)
        gpus.append({'id': i, 'temperature': temp})
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

@app.route('/api/cpu_user_rank')
def cpu_user_rank():
    users = [f'user{i+1}' for i in range(20)]
    selected_users = random.sample(users, 5)
    # 차이 극대화: [0~1] 사이 난수의 3제곱(분포가 뾰족해짐)
    raw = [random.random() **4.5 for _ in range(5)]  #0.4제곱이면 1에 가까운 값 많아짐
    # 더 강하게: [random.random() ** exp for exp in (0.3~2)]로 조정 가능
    total = sum(raw)
    normalized = [round(v / total *100, 1) for v in raw]
    # 합 보정
    diff =100.0 - sum(normalized)
    normalized[-1] = round(normalized[-1] + diff, 1)

    data = [
        {'user': u, 'cpu': val}
        for u, val in zip(selected_users, normalized)
    ]
    # (정렬 필요하면 요청하신 방식대로)
    data = sorted(data, key=lambda x: x['cpu'], reverse=True)
    return jsonify({'users': data})

@app.route('/api/gpu_user_rank')
def gpu_user_rank():
    users = [f'user{i+1}' for i in range(20)]
    selected_users = random.sample(users, 5)
    # 차이 극대화: [0~1] 사이 난수의 3제곱(분포가 뾰족해짐)
    raw = [random.random() **4.5 for _ in range(5)]  #0.4제곱이면 1에 가까운 값 많아짐
    # 더 강하게: [random.random() ** exp for exp in (0.3~2)]로 조정 가능
    total = sum(raw)
    normalized = [round(v / total *100, 1) for v in raw]
    # 합 보정
    diff =100.0 - sum(normalized)
    normalized[-1] = round(normalized[-1] + diff, 1)

    data = [
        {'user': u, 'gpu': val}
        for u, val in zip(selected_users, normalized)
    ]
    data = sorted(data, key=lambda x: x['gpu'], reverse=True)
    return jsonify({'users': data})

@app.route('/api/mem_user_rank')
def mem_user_rank():
    users = [f'user{i+1}' for i in range(20)]
    selected_users = random.sample(users, 5)
    # 차이 극대화: [0~1] 사이 난수의 3제곱(분포가 뾰족해짐)
    raw = [random.random() **4.5 for _ in range(5)]  #0.4제곱이면 1에 가까운 값 많아짐
    # 더 강하게: [random.random() ** exp for exp in (0.3~2)]로 조정 가능
    total = sum(raw)
    normalized = [round(v / total *100, 1) for v in raw]
    # 합 보정
    diff =100.0 - sum(normalized)
    normalized[-1] = round(normalized[-1] + diff, 1)

    data = [
        {'user': u, 'mem': val}
        for u, val in zip(selected_users, normalized)
    ]
    # (정렬 필요하면 요청하신 방식대로)
    data = sorted(data, key=lambda x: x['mem'], reverse=True)
    return jsonify({'users': data})


@app.route('/api/idle_user_rank')
def idle_user_rank():
    import random
    users = [f'user{i+1}' for i in range(20)]
    data = sorted(
        [{'user': u, 'idle': int(random.uniform(0, 500))} for u in users],
        key=lambda x: x['idle'],
        reverse=True
    )[:5]
    return jsonify({'users': data})

if __name__ == '__main__':
    app.run('0.0.0.0', port=8000, debug=True)