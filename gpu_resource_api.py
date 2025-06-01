# gpu_resource_api.py
from flask import Flask, jsonify, request
from datetime import datetime, timedelta

app = Flask(__name__)

# 더미 GPU 자원 데이터
gpu_resources = [
    {"gpu_id": 0, "user": "홍길동", "start_date": "2024-05-20", "end_date": "2024-06-20"},
    {"gpu_id": 1, "user": "김철수", "start_date": "2024-05-22", "end_date": "2024-06-22"},
]

# 자원 정책
resource_policy = {
    "max_days": 30,
    "user_limit": 2
}

@app.route("/api/resources", methods=["GET"])
def get_resources():
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
    # 예시: 기간별 사용량 더미 데이터
    return jsonify({
        "labels": ["5월", "6월"],
        "usage": [20, 18]
    })

@app.route("/api/reports/idle", methods=["GET"])
def report_idle():
    # 예시: GPU별 유휴 시간 더미 데이터
    return jsonify({
        "labels": ["GPU0", "GPU1"],
        "idle": [5, 2]
    })

if __name__ == "__main__":
    app.run(debug=True)
