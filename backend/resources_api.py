from flask import Blueprint, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import random

app = Blueprint('resources_api', __name__)
CORS(app)

# --- USERS (이름만) ---
users = [
    "홍길동", "김철수", "김동현", "김서권", "윤다빈",
    "박지훈", "최예린", "이민호", "한지수", "조윤호",
    "정소연", "오세훈", "서지수", "배상우", "노지윤"
]

# --- 자원 목록 (기본 정보만, 할당X) ---
gpu_models = ["RTX 4090", "A100", "RTX 4080", "L40S"] * 5
cpu_models = ["Intel Xeon Gold 6338", "AMD EPYC 7543P"] * 10
GPU_COUNT = 20
CPU_COUNT = 20
MEMORY_COUNT = 20
resources = []
for i in range(GPU_COUNT):
    resources.append({"res_id": i, "type": "GPU", "model": gpu_models[i % len(gpu_models)]})
for i in range(CPU_COUNT):
    resources.append({"res_id": i, "type": "CPU", "model": cpu_models[i % len(cpu_models)]})
for i in range(MEMORY_COUNT):
    resources.append({"res_id": i, "type": "Memory", "model": "DDR4-3200 1TB"})

# --- allocations : 랜덤 더미로 미리 할당해둠 ---
allocations = []
today = datetime(2025, 6, 16)
for i, u in enumerate(users[:7]):
    s = today - timedelta(days=random.randint(1, 200))
    e = s + timedelta(days=random.randint(3, 20))
    allocations.append({"res_id": i, "type": "GPU", "user": u, "start_date": s.strftime("%Y-%m-%d"), "end_date": e.strftime("%Y-%m-%d")})
for i, u in enumerate(users[7:11]):
    s = today - timedelta(days=random.randint(1, 200))
    e = s + timedelta(days=random.randint(3, 20))
    allocations.append({"res_id": i, "type": "CPU", "user": u, "start_date": s.strftime("%Y-%m-%d"), "end_date": e.strftime("%Y-%m-%d")})
for i, u in enumerate(users[11:14]):
    s = today - timedelta(days=random.randint(1, 200))
    e = s + timedelta(days=random.randint(3, 20))
    allocations.append({"res_id": i, "type": "Memory", "user": u, "start_date": s.strftime("%Y-%m-%d"), "end_date": e.strftime("%Y-%m-%d")})

@app.route("/api/resources", methods=["GET"])
def get_resources():
    result = []
    for r in resources:
        alloc = next((a for a in allocations if a["res_id"] == r["res_id"] and a["type"] == r["type"]), None)
        row = {**r}
        if alloc:
            row.update({k: alloc[k] for k in ["user", "start_date", "end_date"]})
        else:
            row.update({"user": None, "start_date": None, "end_date": None})
        result.append(row)
    return jsonify(result)

@app.route("/api/allocations", methods=["POST"])
def allocate_resource():
    data = request.json
    for a in allocations:
        if a["res_id"] == data["res_id"] and a["type"] == data["type"]:
            return jsonify({"result": "already_allocated"})
    allocations.append({
        "res_id": data["res_id"],
        "type": data["type"],
        "user": data["user"],
        "start_date": data["start_date"],
        "end_date": data["end_date"]
    })
    return jsonify({"result": "success"})

@app.route("/api/allocations/reclaim", methods=["POST"])
def reclaim_resource():
    data = request.json
    global allocations
    allocations = [a for a in allocations if not (a["res_id"] == data["res_id"] and a["type"] == data["type"])]
    return jsonify({"result": "success"})

@app.route("/api/users", methods=["GET"])
def get_users():
    return jsonify(users)

# === 아래는 보고서 및 차트 등 예시 엔드포인트 ===

# (여기부터는 기존 참고용 차트/리포트 등 API 그대로 두었으니, 프론트에서 쓸 수 있음)

today = datetime(2025, 6, 16)
days = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(365)][::-1]

def random_date():
    s = datetime(2025, 1, 1) + timedelta(days=random.randint(0, 300))
    e = s + timedelta(days=random.randint(2, 10))
    return s.strftime("%Y-%m-%d"), e.strftime("%Y-%m-%d")

gpu_temp_history = {}
for i in range(GPU_COUNT):
    temps = []
    base = 35 + i % 5
    for d in days:
        t = base + random.randint(0, 6) + random.randint(-3, 3)
        t = max(35, min(t, 90))
        temps.append(t)
    gpu_temp_history[f"GPU{i}"] = {"dates": days, "temps": temps}

@app.route("/api/report/sysinfo")
def report_sysinfo():
    gpu_used = len([a for a in allocations if a["type"] == "GPU"])
    cpu_used = len([a for a in allocations if a["type"] == "CPU"])
    memory_used = len([a for a in allocations if a["type"] == "Memory"])
    user_count = len(users)
    user_active = random.randint(int(user_count*0.4), int(user_count*0.8))
    user_inactive = user_count - user_active
    return jsonify({
        "user_count": len(users),
        "user_active": user_active,
        "user_inactive": user_inactive,
        "gpu_count": GPU_COUNT,
        "gpu_models": sorted(list(set([r["model"] for r in resources if r["type"] == "GPU"]))),
        "gpu_used": gpu_used,
        "cpu_count": CPU_COUNT,
        "cpu_models": sorted(list(set([r["model"] for r in resources if r["type"] == "CPU"]))),
        "cpu_used": cpu_used,
        "memory_count": MEMORY_COUNT,
        "memory_total_tb": MEMORY_COUNT,
        "memory_used": memory_used
    })

@app.route("/api/report/status")
def report_status():
    gpu_names = [f"GPU{i}" for i in range(GPU_COUNT)]
    cpu_names = [f"CPU{i}" for i in range(CPU_COUNT)]
    memory_names = [f"Memory{i}" for i in range(MEMORY_COUNT)]
    gpu_temps = [gpu_temp_history[f"GPU{i}"]["temps"][-1] for i in range(GPU_COUNT)]
    cpu_temps = [random.randint(35, 80) for _ in range(CPU_COUNT)]
    memory_usages = [random.randint(10, 80) for _ in range(MEMORY_COUNT)]
    return jsonify({
        "gpu_names": gpu_names,
        "cpu_names": cpu_names,
        "memory_names": memory_names,
        "gpu_temps": gpu_temps,
        "cpu_temps": cpu_temps,
        "memory_usages": memory_usages
    })

@app.route("/api/report/total_usage")
def report_total_usage():
    start = request.args.get("start")
    end = request.args.get("end")
    _days = days
    if start and end and len(start) == 8 and len(end) == 8:
        _days = [d for d in days if start <= d.replace("-", "") <= end]
    usage = {"gpu": [], "cpu": [], "memory": []}
    for d in _days:
        cnt = {"GPU": 0, "CPU": 0, "Memory": 0}
        for a in allocations:
            s = datetime.strptime(a["start_date"], "%Y-%m-%d")
            e = datetime.strptime(a["end_date"], "%Y-%m-%d")
            cur = datetime.strptime(d, "%Y-%m-%d")
            if s <= cur <= e:
                cnt[a["type"]] += 1
        usage["gpu"].append(cnt["GPU"])
        usage["cpu"].append(cnt["CPU"])
        usage["memory"].append(cnt["Memory"])
    return jsonify({"dates": _days, **usage})

@app.route("/api/report/individual_usage")
def report_individual_usage():
    typ = request.args.get('type')
    name = request.args.get('name')
    start = request.args.get('start')
    end = request.args.get('end')
    idx = int(name.replace(typ, "")) if name and name.replace(typ, "").isdigit() else 0
    _days = days
    if start and end and len(start) == 8 and len(end) == 8:
        _days = [d for d in days if start <= d.replace("-", "") <= end]
    values = []
    for d in _days:
        alloc = next((a for a in allocations if a["res_id"] == idx and a["type"] == typ), None)
        if alloc:
            s = datetime.strptime(alloc["start_date"], "%Y-%m-%d")
            e = datetime.strptime(alloc["end_date"], "%Y-%m-%d")
            cur = datetime.strptime(d, "%Y-%m-%d")
            values.append(1 if s <= cur <= e else 0)
        else:
            values.append(round(random.uniform(0, 0.3), 2))
    return jsonify({"dates": _days, "values": values})

@app.route("/api/report/gpu_temp_series")
def report_gpu_temp_series():
    name = request.args.get('name', 'GPU0')
    start = request.args.get('start')
    end = request.args.get('end')
    hist = gpu_temp_history.get(name, None)
    if not hist:
        return jsonify({"dates": days, "temps": [40] * len(days)})
    _dates = hist["dates"]
    _temps = hist["temps"]
    if start and end and len(start) == 8 and len(end) == 8:
        zipped = [(d, t) for d, t in zip(_dates, _temps) if start <= d.replace("-", "") <= end]
        if zipped:
            _dates, _temps = zip(*zipped)
    return jsonify({"dates": list(_dates), "temps": list(_temps)})

@app.route("/api/report/rank")
def report_rank():
    usage_dict = {u: {"gpu":0, "cpu":0, "memory":0} for u in users}
    idle_dict = {u: 0 for u in users}
    for a in allocations:
        s = datetime.strptime(a["start_date"], "%Y-%m-%d")
        e = datetime.strptime(a["end_date"], "%Y-%m-%d")
        days_used = (e - s).days + 1
        usage_dict[a["user"]][a["type"].lower()] += days_used
    for u in users:
        used_days = usage_dict[u]["gpu"] + usage_dict[u]["cpu"] + usage_dict[u]["memory"]
        idle_dict[u] = max(0, 365*3 - used_days)
    usage_rank = sorted(
        [{"name":u, **usage_dict[u]} for u in users],
        key=lambda x: x["gpu"]+x["cpu"]+x["memory"],
        reverse=True
    )[:5]
    idle_rank = sorted(
        [{"name":u, "idle":idle_dict[u]} for u in users],
        key=lambda x: x["idle"],
        reverse=True
    )[:5]
    return jsonify({"usage": usage_rank, "idle": idle_rank})

# --- ChartJS 스타일의 멀티/싱글 (예시, 1년치 1시간단위) ---
_multi_series = []
_single_series = []
start_time = datetime(today.year, 1, 1)
for i in range(24*365):
    ts = (start_time + timedelta(hours=i)).strftime('%Y-%m-%dT%H:%M:%S')
    _multi_series.append({
        "timestamp": ts,
        "datas": [{"id": idx, "value": random.randint(0, 100)} for idx in range(4)]
    })
    _single_series.append({
        "timestamp": ts,
        "value": random.randint(0, 100)
    })

@app.route("/api/chartjs/multi")
def chartjs_multi():
    start = request.args.get("start")
    end = request.args.get("end")
    result = _multi_series
    if start and end:
        result = [r for r in _multi_series if start <= r["timestamp"][:10].replace("-", "") <= end]
    return jsonify(result)

@app.route("/api/chartjs/single")
def chartjs_single():
    start = request.args.get("start")
    end = request.args.get("end")
    result = _single_series
    if start and end:
        result = [r for r in _single_series if start <= r["timestamp"][:10].replace("-", "") <= end]
    return jsonify(result)