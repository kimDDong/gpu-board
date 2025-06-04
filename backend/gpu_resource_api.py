from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True,
     allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
     expose_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"])

# 고정 유저 5명 (더미)
users = [
    "홍길동", "김철수", "이영희", "박민수", "최수연"
]

# GPU 자원 더미 (각 사용자 2개씩, 유휴 4명)
gpu_resources = [
    # 홍길동
    {"gpu_id": 0, "user": "홍길동", "start_date": "2025-05-01", "end_date": "2025-05-10"},  # 유휴 (24일 전 만료)
    {"gpu_id": 1, "user": "홍길동", "start_date": "2025-07-10", "end_date": "2025-07-18"},

    # 김철수
    {"gpu_id": 2, "user": "김철수", "start_date": "2025-05-05", "end_date": "2025-05-30"},  # 유휴 (4일 전 만료)
    {"gpu_id": 3, "user": "김철수", "start_date": "2025-07-05", "end_date": "2025-07-12"},

    # 이영희
    {"gpu_id": 4, "user": "이영희", "start_date": "2025-04-20", "end_date": "2025-05-31"},  # 유휴 (3일 전 만료)
    {"gpu_id": 5, "user": "이영희", "start_date": "2025-07-15", "end_date": "2025-07-22"},

    # 박민수
    {"gpu_id": 6, "user": "박민수", "start_date": "2025-06-01", "end_date": "2025-06-15"},  # 만료일 미래(유휴X)
    {"gpu_id": 7, "user": "박민수", "start_date": "2025-05-20", "end_date": "2025-05-25"},  # 유휴 (9일 전 만료)

    # 최수연
    {"gpu_id": 8, "user": "최수연", "start_date": "2025-07-01", "end_date": "2025-07-10"},
    {"gpu_id": 9, "user": "최수연", "start_date": "2025-06-05", "end_date": "2025-06-20"},  # 만료일 미래(유휴X)
]

resource_policy = {"max_days": 30, "user_limit": 2}

@app.route("/api/resources", methods=["GET"])
def get_resources():
    return jsonify(gpu_resources)

@app.route("/api/resources", methods=["POST"])
def add_resource():
    global gpu_resources
    data = request.json
    new_id = max([r['gpu_id'] for r in gpu_resources], default=-1) + 1
    gpu_resources.append({
        "gpu_id": new_id,
        "user": data["user"],
        "start_date": data["start_date"],
        "end_date": data["end_date"]
    })
    return jsonify({"result": "success"})

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

@app.route("/api/users", methods=["GET"])
def get_users():
    return jsonify(users)

@app.route("/api/reports/usage", methods=["GET"])
def report_usage():
    from datetime import datetime, timedelta
    user_stats = {u: 0 for u in users}
    daily_stats = {}

    date_range = [
        (datetime(2025,7,1) + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(31)
    ]
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

if __name__ == "__main__":
    app.run(debug=True)
