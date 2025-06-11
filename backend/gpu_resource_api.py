from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import random

app = Flask(__name__)
CORS(app)

users = ["홍길동", "김철수", "이영희", "박민수", "최수연"]
resources = [{'res_id': i, 'type': 'GPU'} for i in range(6)] + \
            [{'res_id': i, 'type': 'CPU'} for i in range(4)] + \
            [{'res_id': i, 'type': 'Memory'} for i in range(3)]

allocations = [
    {"res_id": 0, "type": "GPU", "user": "홍길동", "start_date": "2024-07-01", "end_date": "2024-07-12"},
    {"res_id": 1, "type": "GPU", "user": "김철수", "start_date": "2024-07-03", "end_date": "2024-07-13"},
    {"res_id": 2, "type": "GPU", "user": "이영희", "start_date": "2024-07-04", "end_date": "2024-07-15"},
    {"res_id": 3, "type": "GPU", "user": "최수연", "start_date": "2024-07-09", "end_date": "2024-07-19"},
    {"res_id": 4, "type": "GPU", "user": "박민수", "start_date": "2024-07-10", "end_date": "2024-07-16"},
    {"res_id": 5, "type": "GPU", "user": "홍길동", "start_date": "2024-07-11", "end_date": "2024-07-17"},
    {"res_id": 0, "type": "CPU", "user": "김철수", "start_date": "2024-07-02", "end_date": "2024-07-08"},
    {"res_id": 1, "type": "CPU", "user": "최수연", "start_date": "2024-07-04", "end_date": "2024-07-11"},
    {"res_id": 2, "type": "CPU", "user": "홍길동", "start_date": "2024-07-06", "end_date": "2024-07-13"},
    {"res_id": 0, "type": "Memory", "user": "이영희", "start_date": "2024-07-01", "end_date": "2024-07-10"},
    {"res_id": 1, "type": "Memory", "user": "박민수", "start_date": "2024-07-05", "end_date": "2024-07-13"}
]

@app.route('/api/sysinfo')
def sysinfo():
    return jsonify({
        'os': 'Ubuntu 22.04',
        'cpu': 'Intel Xeon Gold 6226R',
        'mem': '256GB',
        'gpu': 'NVIDIA RTX A6000 x6'
    })

@app.route("/api/resources")
def get_resources():
    result = []
    for r in resources:
        alloc = next((a for a in allocations if a['res_id'] == r['res_id'] and a['type'] == r['type']), None)
        row = {**r, **(alloc if alloc else {'user': None, 'start_date': None, 'end_date': None})}
        result.append(row)
    return jsonify(result)

@app.route("/api/users")
def get_users():
    return jsonify(users)

@app.route("/api/allocations", methods=["POST"])
def allocate():
    data = request.json
    if any(a for a in allocations if a['res_id'] == data['res_id'] and a['type'] == data['type']):
        return jsonify({"result": "already_allocated"})
    allocations.append({
        'res_id': data['res_id'],
        'type': data['type'],
        'user': data['user'],
        'start_date': data['start_date'],
        'end_date': data['end_date']
    })
    return jsonify({"result": "success"})

@app.route("/api/allocations/reclaim", methods=["POST"])
def reclaim():
    data = request.json
    global allocations
    allocations = [a for a in allocations if not (a['res_id'] == data['res_id'] and a['type'] == data['type'])]
    return jsonify({"result": "success"})

@app.route("/api/reports/summary")
def summary():
    stats = {}
    for t in ['GPU', 'CPU', 'Memory']:
        total = len([r for r in resources if r['type'] == t])
        used = len([a for a in allocations if a['type'] == t])
        stats[t] = {
            'total': total,
            'used': used,
            'idle': total - used,
            'used_percent': round(used / total * 100) if total else 0
        }
    return jsonify(stats)

@app.route("/api/period_stats")
def period_stats():
    start_str = request.args.get('start')
    end_str = request.args.get('end')
    gpus = request.args.getlist('gpus')
    today = datetime.today()
    start = datetime.strptime(start_str, "%Y-%m-%d") if start_str else today - timedelta(days=6)
    end = datetime.strptime(end_str, "%Y-%m-%d") if end_str else today
    dates = [(start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range((end - start).days + 1)]
    cpu = [random.randint(45, 97) for _ in dates]
    mem = [random.randint(120, 250) for _ in dates]
    gpu_idxs = list(map(int, gpus)) if gpus else list(range(6))
    gpu_lines = [[random.randint(35 + 4*idx, 88 - 3*idx) for _ in dates] for idx in gpu_idxs]
    gpu_labels = [f"GPU {i}" for i in gpu_idxs]
    gpu_total = [sum(g[i] for g in gpu_lines) // max(len(gpu_lines), 1) for i in range(len(dates))] if gpu_lines else [0 for _ in dates]
    return jsonify({
        'dates': dates,
        'cpu': cpu,
        'mem': mem,
        'gpu': gpu_lines,
        'gpu_labels': gpu_labels,
        'gpu_total': gpu_total
    })

@app.route("/api/gpus")
def list_gpus():
    return jsonify([
        {
            'id': i,
            'name': f'GPU {i}',
            'temp': random.randint(49 + i*2, 76 + i*2),
            'usage': random.randint(23 + i*4, 89 - i*3)
        } for i in range(6)
    ])

@app.route("/api/user_rank")
def user_rank():
    usage = {u: 0 for u in users}
    for a in allocations:
        if a['type'] == 'GPU':
            d1 = datetime.strptime(a['start_date'], "%Y-%m-%d")
            d2 = datetime.strptime(a['end_date'], "%Y-%m-%d")
            usage[a['user']] += (d2 - d1).days + 1
    usage_list = [{'name': u, 'usage': usage[u] + random.randint(3, 12)} for u in users]
    usage_list.sort(key=lambda x: -x['usage'])
    return jsonify(usage_list)

@app.route("/api/user_idle_rank")
def user_idle():
    idle = {u: random.randint(30, 80) for u in users}
    for a in allocations:
        if a['type'] == 'GPU':
            idle[a['user']] -= random.randint(4, 12)
    idle_list = [{'name': u, 'idle': max(0, idle[u])} for u in users]
    idle_list.sort(key=lambda x: -x['idle'])
    return jsonify(idle_list)

@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(debug=True)
