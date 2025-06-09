from flask import Flask, jsonify, request
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

# 사용자 목록 저장소 (메모리 기반)
users = []

names = [
    '홍길동', '김철수', '김동현', '김서권', '윤다빈',
    '박지훈', '최예린', '이민호', '한지수', '조윤호',
    '정소연', '오세훈', '서지수', '배상우', '노지윤'
]

roles = ['관리자', '일반 사용자']

# 초기 사용자 생성
for i in range(15):
    users.append({
        "id": f"user{i + 1}",
        "name": names[i],
        "role": roles[i % 2],
        "cpuUsage": [random.randint(10, 90) for _ in range(31)],
        "gpuUsage": [random.randint(10, 90) for _ in range(31)],
        "memUsage": [random.randint(10, 90) for _ in range(31)],
        "usageTimestamps": [str(d) for d in range(1, 32)]
    })

# 역할별 권한 저장소
role_permissions = {}

# 사용자 목록 조회
@app.route('/api/users', methods=['GET'])
def get_users():
    return jsonify(users)

# 사용자 추가
@app.route('/api/users', methods=['POST'])
def add_user():
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
    users.append(new_user)
    return jsonify({"user": new_user}), 201

# 사용자 삭제
@app.route('/api/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    global users
    users = [u for u in users if u["id"] != user_id]
    return jsonify({"message": "삭제 완료"})

# 사용자 수정
@app.route('/api/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    for user in users:
        if user["id"] == user_id:
            user.update({
                "name": data.get("name", user["name"]),
                "role": data.get("role", user["role"])
            })
            return jsonify({"user": user})
    return jsonify({"message": "사용자 없음"}), 404

# 역할별 권한 저장
@app.route('/api/roles', methods=['POST'])
def save_permissions():
    data = request.get_json()
    role_permissions[data["role"]] = data.get("permissions", [])
    return jsonify({"message": "저장 완료"})

# 역할별 권한 조회
@app.route('/api/roles/<role>', methods=['GET'])
def get_permissions(role):
    return jsonify({
        "role": role,
        "permissions": role_permissions.get(role, [])
    })

if __name__ == '__main__':
    app.run(port=5002)
