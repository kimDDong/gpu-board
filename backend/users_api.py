from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 임시 사용자 저장소
users = [
    {"id": "user1", "name": "홍길동", "role": "관리자"},
    {"id": "user2", "name": "김철수", "role": "일반 사용자"}
]

# 사용자 목록 조회
@app.route('/api/users', methods=['GET'])
def get_users():
    return jsonify(users)

# 사용자 추가 (POST)
@app.route('/api/users', methods=['POST'])
def add_user():
    data = request.get_json()
    users.append({
        "id": data["id"],
        "name": data["name"],
        "role": data["role"]
    })
    return jsonify({"message": "사용자 추가 완료", "user": data}), 201

# 사용자 삭제
@app.route('/api/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    global users
    users = [u for u in users if u["id"] != user_id]
    return jsonify({"message": f"{user_id} 삭제 완료"}), 200

# 사용자 수정
@app.route('/api/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    for user in users:
        if user["id"] == user_id:
            user["name"] = data.get("name", user["name"])
            user["role"] = data.get("role", user["role"])
            return jsonify({"message": "수정 완료", "user": user}), 200
    return jsonify({"message": "사용자를 찾을 수 없음"}), 404

# 역할별 권한 저장소 (메모리)
role_permissions = {}

# 역할 권한 저장 (create/update)
@app.route('/api/roles', methods=['POST'])
def save_role_permissions():
    data = request.get_json()
    role = data.get("role")
    permissions = data.get("permissions", [])
    role_permissions[role] = permissions
    return jsonify({"message": f"{role} 권한 저장 완료"}), 200

# 역할별 권한 조회
@app.route('/api/roles/<role>', methods=['GET'])
def get_role_permissions(role):
    perms = role_permissions.get(role, [])
    return jsonify({"role": role, "permissions": perms})


if __name__ == '__main__':
    app.run(port=5002)
