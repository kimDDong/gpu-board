
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import random
import math
import time

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True,
     allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
     expose_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"])

# ---------------------- SYSTEM MONITORING API ----------------------

@app.route('/api/cpu/count')
def cpu_count():
    return jsonify({"value": random.randint(4, 32)})

@app.route('/api/cpu/util')
def cpu_util():
    x = time.time() / 7
    value = (math.sin(x) + 1) / 2 * 100
    return jsonify({"value": round(value, 1)})

@app.route('/api/cpu/core_util')
def cpu_core_util():
    core_count = 12
    cores = [{'id': i, 'usage': round(random.uniform(0, 100), 1)} for i in range(core_count)]
    return jsonify({"cores": cores})

@app.route('/api/gpu/count')
def gpu_count():
    return jsonify({"value": random.randint(0, 8)})

@app.route('/api/gpu/util')
def gpu_util():
    return jsonify({"value": random.randint(0, 100)})

@app.route('/api/gpu/util_detail')
def gpu_util_detail():
    gpu_count = 6
    now = time.time()
    gpus = []
    for i in range(gpu_count):
        phase = i * (2 * math.pi / gpu_count)
        value = (math.sin(now / 7 + phase) + 1) / 2 * 100
        gpus.append({'id': i, 'usage': round(value, 1)})
    return jsonify({"gpus": gpus})

@app.route('/api/gpu/temp_detail')
def gpu_temp_detail():
    gpus = [{'id': i, 'temperature': round(random.uniform(30, 200), 1)} for i in range(6)]
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

# ---------------------- USER RANKING API ----------------------

def generate_user_rank(metric):
    users = [f'user{i+1}' for i in range(20)]
    selected_users = random.sample(users, 5)
    raw = [random.random() ** 4.5 for _ in range(5)]
    total = sum(raw)
    normalized = [round(v / total * 100, 1) for v in raw]
    diff = 100.0 - sum(normalized)
    normalized[-1] = round(normalized[-1] + diff, 1)
    data = [{'user': u, metric: val} for u, val in zip(selected_users, normalized)]
    data.sort(key=lambda x: x[metric], reverse=True)
    return jsonify({'users': data})

@app.route('/api/cpu_user_rank')
def cpu_user_rank():
    return generate_user_rank('cpu')

@app.route('/api/gpu_user_rank')
def gpu_user_rank():
    return generate_user_rank('gpu')

@app.route('/api/mem_user_rank')
def mem_user_rank():
    return generate_user_rank('mem')

@app.route('/api/idle_user_rank')
def idle_user_rank():
    users = [f'user{i+1}' for i in range(20)]
    data = sorted([{'user': u, 'idle': int(random.uniform(0, 500))} for u in users], key=lambda x: x['idle'], reverse=True)[:5]
    return jsonify({'users': data})

# ---------------------- GPU RESOURCE MANAGEMENT ----------------------

users_fixed = ["홍길동", "김철수", "이영희", "박민수", "최수연"]
gpu_resources = [
    {"gpu_id": 0, "user": "홍길동", "start_date": "2025-05-01", "end_date": "2025-05-10"},
    {"gpu_id": 1, "user": "홍길동", "start_date": "2025-07-10", "end_date": "2025-07-18"},
    {"gpu_id": 2, "user": "김철수", "start_date": "2025-05-05", "end_date": "2025-05-30"},
    {"gpu_id": 3, "user": "김철수", "start_date": "2025-07-05", "end_date": "2025-07-12"},
    {"gpu_id": 4, "user": "이영희", "start_date": "2025-04-20", "end_date": "2025-05-31"},
    {"gpu_id": 5, "user": "이영희", "start_date": "2025-07-15", "end_date": "2025-07-22"},
    {"gpu_id": 6, "user": "박민수", "start_date": "2025-06-01", "end_date": "2025-06-15"},
    {"gpu_id": 7, "user": "박민수", "start_date": "2025-05-20", "end_date": "2025-05-25"},
    {"gpu_id": 8, "user": "최수연", "start_date": "2025-07-01", "end_date": "2025-07-10"},
    {"gpu_id": 9, "user": "최수연", "start_date": "2025-06-05", "end_date": "2025-06-20"},
]
resource_policy = {"max_days": 30, "user_limit": 2}

@app.route("/api/resources", methods=["GET", "POST"])
def manage_resources():
    global gpu_resources
    if request.method == "POST":
        data = request.json
        new_id = max([r['gpu_id'] for r in gpu_resources], default=-1) + 1
        gpu_resources.append({
            "gpu_id": new_id,
            "user": data["user"],
            "start_date": data["start_date"],
            "end_date": data["end_date"]
        })
        return jsonify({"result": "success"})
    return jsonify(gpu_resources)

@app.route("/api/resources/<int:gpu_id>/reclaim", methods=["POST"])
def reclaim_resource(gpu_id):
    global gpu_resources
    gpu_resources = [r for r in gpu_resources if r["gpu_id"] != gpu_id]
    return jsonify({"result": "success"})

@app.route("/api/resources/<int:gpu_id>/period", methods=["PATCH"])
def update_period(gpu_id):
    data = request.json
    for r in gpu_resources:
        if r["gpu_id"] == gpu_id:
            r["end_date"] = data.get("end_date", r["end_date"])
    return jsonify({"result": "success"})

@app.route("/api/policy", methods=["GET", "POST"])
def policy():
    global resource_policy
    if request.method == "POST":
        resource_policy["max_days"] = int(request.json.get("max_days", resource_policy["max_days"]))
        resource_policy["user_limit"] = int(request.json.get("user_limit", resource_policy["user_limit"]))
    return jsonify(resource_policy)

@app.route("/api/reports/usage", methods=["GET"])
def report_usage():
    user_stats = {u: 0 for u in users_fixed}
    daily_stats = {}
    date_range = [(datetime(2025, 7, 1) + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(31)]
    for d in date_range:
        daily_stats[d] = 0
    for r in gpu_resources:
        s = datetime.strptime(r["start_date"], "%Y-%m-%d")
        e = datetime.strptime(r["end_date"], "%Y-%m-%d")
        days = (e - s).days + 1
        user_stats[r["user"]] += days
        for day in date_range:
            day_dt = datetime.strptime(day, "%Y-%m-%d")
            if s <= day_dt <= e:
                daily_stats[day] += 1
    return jsonify({
        "users": list(user_stats.keys()),
        "user_usage": list(user_stats.values()),
        "dates": date_range,
        "daily_usage": list(daily_stats.values()),
        "total_usage": sum(user_stats.values())
    })

@app.route("/api/reports/idle", methods=["GET"])
def report_idle():
    now = datetime.now()
    gpu_idle = []
    for r in gpu_resources:
        end_dt = datetime.strptime(r["end_date"], "%Y-%m-%d")
        idle = (now - end_dt).days if end_dt < now else 0
        gpu_idle.append({"gpu_id": r["gpu_id"], "user": r["user"], "idle_days": idle})
    return jsonify(gpu_idle)

# ---------------------- USER CRUD API ----------------------

users_dynamic = []
names = ['홍길동', '김철수', '김동현', '김서권', '윤다빈', '박지훈', '최예린', '이민호', '한지수', '조윤호', '정소연', '오세훈', '서지수', '배상우', '노지윤']
roles = ['관리자', '일반 사용자']
role_permissions = {}

for i in range(15):
    users_dynamic.append({
        "id": f"user{i + 1}",
        "name": names[i],
        "role": roles[i % 2],
        "cpuUsage": [random.randint(10, 90) for _ in range(31)],
        "gpuUsage": [random.randint(10, 90) for _ in range(31)],
        "memUsage": [random.randint(10, 90) for _ in range(31)],
        "usageTimestamps": [str(d) for d in range(1, 32)]
    })

@app.route('/api/users', methods=['GET', 'POST'])
def manage_users():
    if request.method == 'POST':
        data = request.get_json()
        new_user = {
            "id": data["id"],
            "name": data["name"],
            "role": data["role"],
            "cpuUsage": [random.randint(10, 90) for _ in range(31)],
            "gpuUsage": [random.randint(10, 90) for _ in range(31)],
            "memUsage": [random.randint(10, 90) for _ in range(31)],
            "usageTimestamps": [str(d) for d in range(1, 32)]
        }
        users_dynamic.append(new_user)
        return jsonify({"user": new_user}), 201
    return jsonify(users_dynamic)

@app.route('/api/users/<user_id>', methods=['DELETE', 'PUT'])
def modify_user(user_id):
    global users_dynamic
    if request.method == 'DELETE':
        users_dynamic = [u for u in users_dynamic if u["id"] != user_id]
        return jsonify({"message": "삭제 완료"})
    else:
        data = request.get_json()
        for user in users_dynamic:
            if user["id"] == user_id:
                user.update({
                    "name": data.get("name", user["name"]),
                    "role": data.get("role", user["role"])
                })
                return jsonify({"user": user})
        return jsonify({"message": "사용자 없음"}), 404

@app.route('/api/roles', methods=['POST'])
def save_permissions():
    data = request.get_json()
    role_permissions[data["role"]] = data.get("permissions", [])
    return jsonify({"message": "저장 완료"})

@app.route('/api/roles/<role>', methods=['GET'])
def get_permissions(role):
    return jsonify({
        "role": role,
        "permissions": role_permissions.get(role, [])
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
