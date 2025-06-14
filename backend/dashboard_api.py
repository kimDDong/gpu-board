from flask import Blueprint, jsonify
import random
import math
import time

app = Blueprint('dashboard_api', __name__)

@app.route('/api/cpu/count')
def cpu_count(): return jsonify({"value": random.randint(4, 32)})

@app.route('/api/gpu/count')
def gpu_count(): return jsonify({"value": random.randint(1, 8)})

@app.route('/api/mem/total')
def mem_total(): return jsonify({"value": random.choice([64, 128, 256, 512])})

@app.route('/api/system/idletime')
def idle_time(): return jsonify({"value": random.randint(1, 10000)})

@app.route('/api/system/uptime')
def up_time(): return jsonify({"value": random.randint(1, 10000)})

@app.route('/api/cpu/usage')
def cpu_usage():
    value = (math.sin(time.time() /7) +1) /2 *100
    return jsonify({"value": round(value, 1)})

@app.route('/api/gpu/usage')
def gpu_usage(): return jsonify({"value": round(random.uniform(20, 100), 1)})

@app.route('/api/mem/usage')
def mem_util(): return jsonify({"value": round(random.uniform(20, 100), 1)})

@app.route('/api/cpu/detail/usage')
def cpu_usage_detail():
    cpu_count =12
    cpus = []
    for i in range(cpu_count):
        usage = round(random.uniform(0, 100), 1)  #0.0 ~100.0, 소수점 1자리
        cpus.append({'id': i, 'value': usage})
    return jsonify({"cpus": cpus})

@app.route('/api/gpu/detail/usage')
def gpu_usage_detail():
    gpu_count = 6
    gpus = []
    now = time.time()
    for i in range(gpu_count):
        phase = i * (2 * math.pi / gpu_count)
        value = (math.sin(now /7 + phase) +1) /2 *100
        gpus.append({'id': i, 'value': round(value, 1)})
    return jsonify({"gpus": gpus})

@app.route('/api/gpu/detail/temp')
def gpu_temp_detail():
    gpu_count = 6
    gpus = []
    for i in range(gpu_count):
        temp = round(random.uniform(30, 200), 1)
        gpus.append({'id': i, 'value': temp})
    return jsonify({"gpus": gpus})

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
        {'user': u, 'value': val}
        for u, val in zip(selected_users, normalized)
    ]
    # (정렬 필요하면 요청하신 방식대로)
    data = sorted(data, key=lambda x: x['value'], reverse=True)
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
        {'user': u, 'value': val}
        for u, val in zip(selected_users, normalized)
    ]
    data = sorted(data, key=lambda x: x['value'], reverse=True)
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
        {'user': u, 'value': val}
        for u, val in zip(selected_users, normalized)
    ]
    # (정렬 필요하면 요청하신 방식대로)
    data = sorted(data, key=lambda x: x['value'], reverse=True)
    return jsonify({'users': data})


@app.route('/api/idle_user_rank')
def idle_user_rank():
    import random
    users = [f'user{i+1}' for i in range(20)]
    data = sorted(
        [{'user': u, 'value': int(random.uniform(0, 500))} for u in users],
        key=lambda x: x['value'],
        reverse=True
    )[:5]
    return jsonify({'users': data})