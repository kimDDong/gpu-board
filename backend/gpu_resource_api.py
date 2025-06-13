from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import random

app = Flask(__name__)
CORS(app)

# ==== 더미 유저/자원 데이터 ====
users = [
    "홍길동", "김철수", "김동현", "김서권", "윤다빈",
    "박지훈", "최예린", "이민호", "한지수", "조윤호",
    "정소연", "오세훈", "서지수", "배상우", "노지윤"
]
gpu_models = ["RTX 4090", "A100", "RTX 4080", "L40S"] * 5
cpu_models = ["Intel Xeon Gold 6338", "AMD EPYC 7543P"] * 10

GPU_COUNT = 20
CPU_COUNT = 20
MEMORY_COUNT = 20  # 1TB씩, 총 20TB

resources = []
for i in range(GPU_COUNT):
    resources.append({"res_id": i, "type": "GPU", "model": gpu_models[i % len(gpu_models)]})
for i in range(CPU_COUNT):
    resources.append({"res_id": i, "type": "CPU", "model": cpu_models[i % len(cpu_models)]})
for i in range(MEMORY_COUNT):
    resources.append({"res_id": i, "type": "Memory", "model": "DDR4-3200 1TB"})

# ==== 할당정보: 랜덤/더미로 생성 ====
def random_date():
    base = datetime(2024, 7, 1)
    s = base + timedelta(days=random.randint(0, 20))
    e = s + timedelta(days=random.randint(2, 10))
    return s.strftime("%Y-%m-%d"), e.strftime("%Y-%m-%d")

allocations = []
for i in range(8):
    s, e = random_date()
    allocations.append({"res_id": i, "type": "GPU", "user": users[i], "start_date": s, "end_date": e})
for i in range(7):
    s, e = random_date()
    allocations.append({"res_id": i, "type": "CPU", "user": users[i+5], "start_date": s, "end_date": e})
for i in range(5):
    s, e = random_date()
    allocations.append({"res_id": i, "type": "Memory", "user": users[i+3], "start_date": s, "end_date": e})

# ==== 시계열 온도 데이터: 날짜별로 생성 ====
gpu_temp_history = {}
days = [f"2024-07-{str(i).zfill(2)}" for i in range(1, 32)]
for i in range(GPU_COUNT):
    temps = []
    base = 35 + i % 5
    for d in days:
        t = base + random.randint(0, 6) + random.randint(-3, 3)
        t = max(35, min(t, 90))
        temps.append(t)
    gpu_temp_history[f"GPU{i}"] = {"dates": days, "temps": temps}

# ==== API ====

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

# ==== REPORT/DASHBOARD ENDPOINTS ====

@app.route("/api/report/sysinfo")
def report_sysinfo():
    # 유저수, 자원수, 모델명 등 요약 + 활동중/오프라인 상태
    gpu_used = len([a for a in allocations if a["type"] == "GPU"])
    cpu_used = len([a for a in allocations if a["type"] == "CPU"])
    memory_used = len([a for a in allocations if a["type"] == "Memory"])
    # 활동중/오프라인: 임의 40~80%를 "활동중"으로 표기
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
    return jsonify({
        "gpu_names": gpu_names,
        "cpu_names": cpu_names,
        "memory_names": memory_names
    })

@app.route("/api/report/total_usage")
def report_total_usage():
    # 각 일자별 전체 사용량(GPU/CPU/Memory)
    dates = days
    usage = {"gpu": [], "cpu": [], "memory": []}
    for d in dates:
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
    return jsonify({"dates": dates, **usage})

@app.route("/api/report/individual_usage")
def report_individual_usage():
    typ = request.args.get('type')
    name = request.args.get('name')
    idx = int(name.replace(typ, "")) if name and name.replace(typ, "").isdigit() else 0
    dates = days
    # 더미: 자원별로 랜덤 사용량(0~1, 단 사용중이면 1)
    values = []
    for d in dates:
        alloc = next((a for a in allocations if a["res_id"] == idx and a["type"] == typ), None)
        if alloc:
            s = datetime.strptime(alloc["start_date"], "%Y-%m-%d")
            e = datetime.strptime(alloc["end_date"], "%Y-%m-%d")
            cur = datetime.strptime(d, "%Y-%m-%d")
            values.append(1 if s <= cur <= e else 0)
        else:
            # 사용중이 아니면 0~0.3 사이 약간의 랜덤 노이즈 (시각화 구색용)
            values.append(round(random.uniform(0, 0.3), 2))
    return jsonify({"dates": dates, "values": values})

@app.route("/api/report/gpu_temp_series")
def report_gpu_temp_series():
    name = request.args.get('name', 'GPU0')
    # 더미: 위에서 만든 gpu_temp_history 사용
    hist = gpu_temp_history.get(name, None)
    if not hist:
        # 이름이 이상할 경우 기본값
        return jsonify({"dates": days, "temps": [40] * len(days)})
    return jsonify(hist)

@app.route("/api/report/rank")
def report_rank():
    # TOP5 누적 사용량, TOP5 누적 유휴(사용하지 않은 기간)
    usage_dict = {u: {"gpu":0, "cpu":0, "memory":0} for u in users}
    idle_dict = {u: 0 for u in users}
    for a in allocations:
        s = datetime.strptime(a["start_date"], "%Y-%m-%d")
        e = datetime.strptime(a["end_date"], "%Y-%m-%d")
        days_used = (e - s).days + 1
        usage_dict[a["user"]][a["type"].lower()] += days_used

    # 유휴일: 전체 기간(31일) - 사용한 일수
    for u in users:
        used_days = usage_dict[u]["gpu"] + usage_dict[u]["cpu"] + usage_dict[u]["memory"]
        idle_dict[u] = max(0, 31*3 - used_days)
    # 랭킹 데이터
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

if __name__ == "__main__":
    app.run(debug=True)
