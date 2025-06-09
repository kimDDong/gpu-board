from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# 더미 유저
users = [
    "홍길동", "김철수", "이영희", "박민수", "최수연"
]

# 자원 더미 데이터 (GPU 15개, CPU 15개)
resources = []
for i in range(15):
    resources.append({"res_id": i, "type": "GPU"})
for i in range(15):
    resources.append({"res_id": i, "type": "CPU"})

# 할당(대여) 정보 (예시)
allocations = [
    # GPU 예시
    {"res_id": 0, "type": "GPU", "user": "홍길동", "start_date": "2024-05-03", "end_date": "2024-05-10"},
    {"res_id": 1, "type": "GPU", "user": "김철수", "start_date": "2024-07-01", "end_date": "2024-07-12"},
    {"res_id": 2, "type": "GPU", "user": "이영희", "start_date": "2024-07-08", "end_date": "2024-07-18"},
    {"res_id": 3, "type": "GPU", "user": "최수연", "start_date": "2024-07-15", "end_date": "2024-07-30"},
    # CPU 예시
    {"res_id": 0, "type": "CPU", "user": "박민수", "start_date": "2024-07-04", "end_date": "2024-07-11"},
    {"res_id": 1, "type": "CPU", "user": "홍길동", "start_date": "2024-07-10", "end_date": "2024-07-20"},
    {"res_id": 2, "type": "CPU", "user": "김철수", "start_date": "2024-06-21", "end_date": "2024-07-09"},
    {"res_id": 3, "type": "CPU", "user": "최수연", "start_date": "2024-07-15", "end_date": "2024-07-25"},
]

# 자원 종류별 정책 (할당 최대일, 사용자별 최대 자원 개수)
resource_policy = {
    "GPU": {"max_days": 30, "user_limit": 2},
    "CPU": {"max_days": 30, "user_limit": 2}
}

@app.route("/api/resources", methods=["GET"])
def get_resources():
    # 전체 자원 + 할당상태 합쳐서 전달
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
    # 기존 동일 자원이 이미 할당돼 있으면 skip (중복 할당 방지)
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

@app.route("/api/policy", methods=["GET", "POST"])
def policy():
    global resource_policy
    if request.method == "POST":
        data = request.json
        for t in ["GPU", "CPU"]:
            if t in data:
                resource_policy[t].update({
                    "max_days": int(data[t].get("max_days", resource_policy[t]["max_days"])),
                    "user_limit": int(data[t].get("user_limit", resource_policy[t]["user_limit"]))
                })
    return jsonify(resource_policy)

@app.route("/api/users", methods=["GET"])
def get_users():
    return jsonify(users)

@app.route("/api/reports/summary", methods=["GET"])
def report_summary():
    summary = {}
    for t in ["GPU", "CPU"]:
        total = len([r for r in resources if r["type"] == t])
        used = len([a for a in allocations if a["type"] == t])
        idle = total - used
        summary[t] = {
            "total": total,
            "used": used,
            "idle": idle,
            "used_percent": round(used/total*100) if total else 0
        }
    return jsonify(summary)

@app.route("/api/reports/heatmap", methods=["GET"])
def report_heatmap():
    # 2024년 7월 한달만 표시
    days = [f"2024-07-{str(i).zfill(2)}" for i in range(1, 32)]
    heatmap = {}
    for t in ["GPU", "CPU"]:
        type_res = [r for r in resources if r["type"] == t]
        data = []
        for r in type_res:
            row = []
            a = next((a for a in allocations if a["res_id"] == r["res_id"] and a["type"] == t), None)
            for d in days:
                if a:
                    s = datetime.strptime(a["start_date"], "%Y-%m-%d")
                    e = datetime.strptime(a["end_date"], "%Y-%m-%d")
                    cur = datetime.strptime(d, "%Y-%m-%d")
                    row.append(1 if s <= cur <= e else 0)
                else:
                    row.append(0)
            data.append({"res_id": r["res_id"], "usage": row})
        heatmap[t] = data
    return jsonify({
        "days": days,
        "heatmap": heatmap
    })

@app.route("/api/reports/usage", methods=["GET"])
def report_usage():
    """
    type=GPU/CPU 쿼리 파라미터 지원. 
    1. 전체 자원(15개) 기준
    2. 2024년 7월(1일~31일) 각 날짜별로, 사용중인 자원 개수
    3. 사용자별, 7월 한달 누적 사용일수
    4. 전체 누적 사용일
    """
    rtype = request.args.get('type', 'GPU')
    dates = [f"2024-07-{str(i).zfill(2)}" for i in range(1, 32)]
    users_in_use = [a["user"] for a in allocations if a["type"] == rtype]
    users_in_use = list(sorted(set(users_in_use)))
    user_usage = {u: 0 for u in users_in_use}
    daily_usage = {d: 0 for d in dates}
    for a in allocations:
        if a["type"] != rtype: continue
        s = datetime.strptime(a["start_date"], "%Y-%m-%d")
        e = datetime.strptime(a["end_date"], "%Y-%m-%d")
        for d in dates:
            day_dt = datetime.strptime(d, "%Y-%m-%d")
            if s <= day_dt <= e:
                daily_usage[d] += 1
                user_usage[a["user"]] += 1
    return jsonify({
        "dates": dates,
        "daily_usage": [daily_usage[d] for d in dates],
        "users": users_in_use,
        "user_usage": [user_usage[u] for u in users_in_use],
        "total_usage": sum(user_usage.values())
    })

@app.route("/api/reports/idle", methods=["GET"])
def report_idle():
    """
    type=GPU/CPU 쿼리 파라미터 지원.
    각 자원별, 현재 기준 유휴 일수 계산
    """
    rtype = request.args.get('type', 'GPU')
    now = datetime.now()
    idle_list = []
    type_res = [r for r in resources if r["type"] == rtype]
    for r in type_res:
        alloc = next((a for a in allocations if a["res_id"] == r["res_id"] and a["type"] == rtype), None)
        if alloc:
            end_dt = datetime.strptime(alloc["end_date"], "%Y-%m-%d")
            idle = (now - end_dt).days if end_dt < now else 0
            user = alloc["user"]
        else:
            idle = 9999
            user = None
        idle_list.append({"res_id": r["res_id"], "user": user, "idle_days": idle})
    return jsonify(idle_list)

if __name__ == "__main__":
    app.run(debug=True)
