from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import random
import math

app = Blueprint('common_api', __name__)


@app.route('/api/simple/1', methods=['GET'])
def simple1():
    start_param = request.args.get('start')
    end_param = request.args.get('end')
    return jsonify({"value": random.randint(0, 100)})

@app.route('/api/simple/2', methods=['GET'])
def simple2():
    start_param = request.args.get('start')
    end_param = request.args.get('end')
    print(start_param)
    return jsonify({"value": [start_param, end_param]})

# --- API ---
'''
url : https://gpu-board.onrender.com/api/chartjs/multi?start=20250101&end=20250330
JSON :
[
    {"timestamp": ... , "datas": [{"id": 0,"value": 0}, ... ]},
    {"timestamp": ... , "datas": [{"id": 0,"value": 0}, ... ]},
    ...
]
'''
@app.route('/api/chartjs/multi', methods=['GET'])
def multi_chart_js():
    start_param = request.args.get('start')
    end_param = request.args.get('end')

    if not start_param or not end_param:
        return jsonify({"error": "Missing 'start' or 'end' query parameters."}), 400

    try:
        start_date_req = datetime.strptime(start_param, "%Y%m%d")
        end_date_req = datetime.strptime(end_param, "%Y%m%d")
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYYMMDD."}), 400
    
    # 미리 생성된 데이터에서 필터링 및 샘플링
    sampled_multi_data = get_sampled_data(PRE_GENERATED_MULTI_DATA, start_date_req, end_date_req)
    return jsonify(sampled_multi_data)

'''
url : https://gpu-board.onrender.com/api/chartjs/single?start=20250101&end=20250330
JSON :
[
    {"timestamp": ... , "datas": "value": 0 },
    {"timestamp": ... , "datas": "value": 0 },
    ...
]
'''
@app.route('/api/chartjs/single', methods=['GET'])
def single_chart_js():
    start_param = request.args.get('start')
    end_param = request.args.get('end')

    if not start_param or not end_param:
        return jsonify({"error": "Missing 'start' or 'end' query parameters."}), 400

    try:
        start_date_req = datetime.strptime(start_param, "%Y%m%d")
        end_date_req = datetime.strptime(end_param, "%Y%m%d")
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYYMMDD."}), 400

    # 미리 생성된 데이터에서 필터링 및 샘플링
    sampled_single_data = get_sampled_data(PRE_GENERATED_SINGLE_DATA, start_date_req, end_date_req)
    return jsonify(sampled_single_data)




# ----------------------------------------------------------------------


# --- 전역 변수: 미리 생성된 데이터 저장 ---
PRE_GENERATED_MULTI_DATA = []
PRE_GENERATED_SINGLE_DATA = []

# --- 데이터 생성 함수 (서버 시작 시 한 번만 호출) ---
def generate_initial_data():
    global PRE_GENERATED_MULTI_DATA, PRE_GENERATED_SINGLE_DATA

    print("서버 시작 시 초기 데이터 생성 중...")

    start_date_gen = datetime(2025, 1, 1, 0, 0, 0)
    end_date_gen = datetime(2025, 12, 31, 23, 59, 59)
    generation_interval = timedelta(hours=1) # 1시간 간격

    # 멀티 차트용 (6개 GPU)
    multi_num = 6
    gpu_states = {}
    for i in range(multi_num):
        gpu_states[i] = {
            'current_usage': random.uniform(5, 15),
            'state': 'IDLE',
            'state_duration_left': 0,
            'target_usage': random.uniform(5, 15)
        }
    
    # 싱글 차트용
    metric_state = {
        'current_usage': random.uniform(5, 15),
        'state': 'IDLE',
        'state_duration_left': 0,
        'target_usage': random.uniform(5, 15)
    }

    current_timestamp = start_date_gen
    while current_timestamp <= end_date_gen:
        # Multi Data 생성
        multi_gpu_data_list = []
        for idx in range(multi_num):
            state_info = gpu_states[idx]

            # 1. 상태 전환 로직
            if state_info['state_duration_left'] <= 0:
                if state_info['state'] == 'IDLE' and random.random() < 0.03: # 상태 전환 확률 (0.05 -> 0.03으로 약간 줄임)
                    if random.random() < 0.7:
                        state_info['state'] = 'BURST'
                        state_info['state_duration_left'] = random.randint(3, 10) # 3-10회
                        state_info['target_usage'] = random.uniform(85, 95) # 버스트 목표 (70-90 -> 85-95로 좀 더 뾰족하게)
                    else:
                        state_info['state'] = 'WORKING'
                        state_info['state_duration_left'] = random.randint(15, 60) # 15-60회
                        state_info['target_usage'] = random.uniform(50, 70) # 작업 목표 (40-70 -> 50-70로 좀 더 높게)
                else:
                    state_info['state'] = 'IDLE'
                    state_info['target_usage'] = random.uniform(5, 15) # IDLE 목표
                # 상태 전환 시 현재 사용률을 새로운 목표에 더 가깝게 초기화
                state_info['current_usage'] = (state_info['current_usage'] + state_info['target_usage']) / 2 

            # 2. 현재 사용률을 목표 사용률로 평활화
            smoothing_factor = 0.15 # 0.2 -> 0.15로 줄여서 더 부드럽게
            # 간격이 짧을 때 변동성을 높이는 로직은 get_sampled_data에서 처리
            
            state_info['current_usage'] += (state_info['target_usage'] - state_info['current_usage']) * smoothing_factor
            
            noise_range_base = 0.5 # 1.0 -> 0.5로 줄여서 노이즈 감소
            state_info['current_usage'] += random.uniform(-noise_range_base, noise_range_base)

            # 사용률을 0-100% 범위 내로 제한
            state_info['current_usage'] = max(0, min(100, state_info['current_usage']))
            state_info['state_duration_left'] -= 1
            
            # 최종 값을 정수로 만들 때 int() 대신 round() 사용
            multi_gpu_data_list.append({"id": idx, "value": round(state_info['current_usage'])}) 
        
        PRE_GENERATED_MULTI_DATA.append({
            "timestamp": current_timestamp.isoformat(timespec='seconds') + 'Z',
            "datas": multi_gpu_data_list
        })

        # Single Data 생성 (멀티와 동일한 로직을 단일 지표에 적용)
        if metric_state['state_duration_left'] <= 0:
            if metric_state['state'] == 'IDLE' and random.random() < 0.03:
                if random.random() < 0.7:
                    metric_state['state'] = 'BURST'
                    metric_state['state_duration_left'] = random.randint(3, 10)
                    metric_state['target_usage'] = random.uniform(85, 95)
                else:
                    metric_state['state'] = 'WORKING'
                    metric_state['state_duration_left'] = random.randint(15, 60)
                    metric_state['target_usage'] = random.uniform(50, 70)
            else:
                metric_state['state'] = 'IDLE'
                metric_state['target_usage'] = random.uniform(5, 15)
            metric_state['current_usage'] = (metric_state['current_usage'] + metric_state['target_usage']) / 2 
        
        smoothing_factor = 0.15
        noise_range_base = 0.5
        metric_state['current_usage'] += (metric_state['target_usage'] - metric_state['current_usage']) * smoothing_factor
        metric_state['current_usage'] += random.uniform(-noise_range_base, noise_range_base)
        metric_state['current_usage'] = max(0, min(100, metric_state['current_usage']))
        metric_state['state_duration_left'] -= 1

        PRE_GENERATED_SINGLE_DATA.append({
            "timestamp": current_timestamp.isoformat(timespec='seconds') + 'Z',
            "value": round(metric_state['current_usage'])
        })

        current_timestamp += generation_interval
    
    print(f"초기 데이터 생성 완료. Multi: {len(PRE_GENERATED_MULTI_DATA)} 샘플, Single: {len(PRE_GENERATED_SINGLE_DATA)} 샘플.")

# --- 데이터 필터링 및 샘플링 함수 ---
# 이 함수는 요청된 기간에 맞춰 미리 생성된 데이터를 다시 샘플링하며,
# 이때 요청 간격(interval_secs)에 따라 추가적인 변동성 조절을 할 수 있습니다.
def get_sampled_data(full_data, start_date_req, end_date_req, max_samples=500):
    filtered_data = [
        item for item in full_data 
        if start_date_req <= datetime.fromisoformat(item['timestamp'].replace('Z', '')) <= end_date_req
    ]
    
    if not filtered_data:
        return []

    num_filtered = len(filtered_data)
    if num_filtered <= max_samples:
        return filtered_data

    # 샘플링 로직
    step = num_filtered / max_samples
    sampled_data = []
    for i in range(max_samples):
        index = math.floor(i * step)
        sampled_data.append(filtered_data[index])
    
    if filtered_data[-1] not in sampled_data:
        sampled_data.append(filtered_data[-1])

    return sampled_data

# --- Flask 앱 시작 시 초기 데이터 생성 ---
generate_initial_data()

# ----------------------------------------------------------------------


# 인메모리 사용자 데이터 저장소
# 키: username (문자열), 값: 사용자 데이터 딕셔너리
users = {}
next_id_counter = 1 # 사용자 데이터 내부의 'id' 필드를 위한 카운터

# --- 헬퍼 함수 ---
# datetime 객체를 ISO 8601 형식의 문자열로 변환 (JSON 응답용)
def format_datetime_for_json(dt_obj):
    if dt_obj:
        return dt_obj.isoformat()
    return None

# 사용 기한에 따라 만료 날짜 계산
def calculate_expiration_date(created_at, usage_period_days):
    if created_at and isinstance(usage_period_days, (int, float)):
        return created_at + timedelta(days=usage_period_days)
    return None
    
# --- 사용자 목록 조회 ---
@app.route('/api/sample/users', methods=['GET']) # 이 경로는 이전과 동일하게 유지됩니다.
def get_all_users():
    all_users_display = []
    for user_data in users.values(): # users 딕셔너리의 값(사용자 데이터)들만 리스트로 변환
        user_display = user_data.copy()
        user_display.pop('password', None) # 보안을 위해 비밀번호는 제외
        user_display['createdAt'] = format_datetime_for_json(user_display['createdAt'])
        user_display['expiredAt'] = format_datetime_for_json(user_display['expiredAt'])
        all_users_display.append(user_display)
    # ID를 기준으로 정렬 (선택 사항)
    all_users_display.sort(key=lambda x: x['id']) # 'id' 필드를 기준으로 정렬
    return jsonify(all_users_display), 200 # 리스트 형태로 반환


# --- 사용자 추가 ---
@app.route('/api/sample/users', methods=['POST'])
def register_user():
    global next_id_counter # id 필드 카운터
    data = request.get_json()

    if not data:
        return jsonify({"message": "JSON 데이터가 필요합니다."}), 400

    username = data.get('username')
    password = data.get('password')
    full_name = data.get('fullName')
    initial_activation = data.get('initialActivation', True) # 기본값 True
    usage_period = data.get('usagePeriod', 30) # 기본값 30

    # 필수 필드 유효성 검사
    if not all([username, password, full_name]):
        return jsonify({"message": "사용자명, 비밀번호, 전체 이름은 필수입니다."}), 400

    # 사용자명 중복 검사 (users 딕셔너리의 키로 확인)
    if username in users:
        return jsonify({"message": "이미 존재하는 사용자명입니다."}), 409 # Conflict

    created_at = datetime.now() # 현재 시간으로 생성 날짜 기록
    expired_at = calculate_expiration_date(created_at, usage_period) # 사용 기한에 따라 만료 날짜 계산

    # 새 사용자 데이터 생성
    new_user = {
        "id": next_id_counter, # 내부 id 필드는 계속 사용
        "username": username,
        "password": password,  # 실제에서는 해싱된 비밀번호를 저장해야 합니다.
        "fullName": full_name,
        "initialActivation": initial_activation,
        "usagePeriod": usage_period,
        "createdAt": created_at, # 생성 날짜 (datetime 객체로 저장)
        "expiredAt": expired_at, # 만료 날짜 (datetime 객체로 저장)
    }
    users[username] = new_user # users 딕셔너리의 키로 username 사용
    next_id_counter += 1

    print(f"등록된 사용자: {new_user}")
    # 응답 시에는 datetime 객체를 문자열로 변환하여 전송
    response_user = new_user.copy()
    response_user.pop('password', None) # 보안을 위해 비밀번호는 응답에서 제외
    response_user['createdAt'] = format_datetime_for_json(response_user['createdAt'])
    response_user['expiredAt'] = format_datetime_for_json(response_user['expiredAt'])

    return jsonify({"message": "사용자 등록 성공", "user": response_user}), 201

# --- 사용자 삭제 API ---
# user_id 대신 username을 경로 변수로 사용
@app.route('/api/sample/users/<string:username>', methods=['DELETE'])
def delete_user(username):
    if username in users:
        deleted_user = users.pop(username)
        print(f"삭제된 사용자: {deleted_user['username']}")
        return jsonify({"message": f"사용자 '{username}'가 성공적으로 삭제되었습니다."}), 200
    return jsonify({"message": "사용자를 찾을 수 없습니다."}), 404

# --- 사용자 정보 조회 ---
# user_id 대신 username을 경로 변수로 사용
@app.route('/api/sample/users/<string:username>', methods=['GET'])
def get_user(username):
    user = users.get(username) # username으로 조회
    if not user:
        return jsonify({"message": "사용자를 찾을 수 없습니다."}), 404

    # 보안을 위해 비밀번호는 응답에서 제외합니다.
    user_display = user.copy()
    user_display.pop('password', None)
    # datetime 객체를 문자열로 변환하여 전송
    user_display['createdAt'] = format_datetime_for_json(user_display['createdAt'])
    user_display['expiredAt'] = format_datetime_for_json(user_display['expiredAt'])
    return jsonify(user_display), 200

# --- 사용자 정보 수정 API ---
# user_id 대신 username을 경로 변수로 사용
@app.route('/api/sample/users/<string:username>', methods=['PATCH'])
def update_user(username):
    user = users.get(username) # username으로 조회
    if not user:
        return jsonify({"message": "사용자를 찾을 수 없습니다."}), 404

    data = request.get_json()

    if not data:
        return jsonify({"message": "JSON 데이터가 필요합니다."}), 400

    usage_period_changed = False
    if 'fullName' in data:
        user['fullName'] = data['fullName']
    if 'initialActivation' in data:
        user['initialActivation'] = data['initialActivation']
    if 'usagePeriod' in data:
        if isinstance(data['usagePeriod'], (int, float)):
            user['usagePeriod'] = int(data['usagePeriod'])
            usage_period_changed = True # 사용 기한이 변경되었음을 표시
        else:
            return jsonify({"message": "사용 기한은 숫자여야 합니다."}), 400
    if 'password' in data and data['password']: # 비밀번호가 전달되었고 비어있지 않으면 업데이트
        user['password'] = data['password'] # 실제에서는 해싱된 비밀번호를 업데이트해야 합니다.

    # usagePeriod가 변경되었으면 expiredAt을 다시 계산
    if usage_period_changed:
        user['expiredAt'] = calculate_expiration_date(user['createdAt'], user['usagePeriod'])

    print(f"업데이트된 사용자: {user}")
    # 보안을 위해 비밀번호는 응답에서 제외합니다.
    response_user = user.copy()
    response_user.pop('password', None)
    # datetime 객체를 문자열로 변환하여 전송
    response_user['createdAt'] = format_datetime_for_json(response_user['createdAt'])
    response_user['expiredAt'] = format_datetime_for_json(response_user['expiredAt'])
    return jsonify({"message": "사용자 정보가 성공적으로 업데이트되었습니다.", "user": response_user}), 200

# ----------------------------------------------------------------------

# 서버 시작 시 임의의 사용자 20명 생성 함수
def generate_dummy_users(num_users=20):
    global next_id_counter
    
    # 생성할 사용자명 리스트 (충돌 방지를 위해 무한 루프 대신 리스트로 관리)
    generated_usernames = []

    for i in range(num_users):
        # 고유한 사용자명 생성
        username = f"dummyuser{next_id_counter:02d}" # 예: dummyuser01, dummyuser02
        # 만약 이미 존재하는 username이라면 다른 방식으로 생성하거나 다음 루프로 넘어갈 수 있습니다.
        # 여기서는 next_id_counter가 계속 증가하므로 고유함이 보장됩니다.
        
        password = "password123" # 테스트용 비밀번호
        full_name = f"더미 사용자 {next_id_counter}"
        initial_activation = random.choice([True, False]) # True 또는 False
        usage_period = random.randint(30, 365) # 30일 ~ 365일 (랜덤)

        # 생성 날짜를 최근 30일 이내의 랜덤 날짜로 설정
        created_at = datetime.now() - timedelta(days=random.randint(0, 30))
        expired_at = calculate_expiration_date(created_at, usage_period)

        new_user_data = {
            "id": next_id_counter,
            "username": username,
            "password": password,
            "fullName": full_name,
            "initialActivation": initial_activation,
            "usagePeriod": usage_period,
            "createdAt": created_at, # 생성 날짜 (datetime 객체)
            "expiredAt": expired_at, # 만료 날짜 (datetime 객체)
        }
        users[username] = new_user_data # username을 키로 사용
        next_id_counter += 1

    print(f"더미 사용자 생성 완료. 현재 사용자 수: {len(users)}")
    print(f"다음 등록될 내부 ID: {next_id_counter}")


generate_dummy_users(20) # 서버 시작 시 더미 사용자 생성

# ----------------------------------------------------------------------


# GPUS = [
#     {"id": "1", "name": "NVIDIA GeForce RTX 4090"},
#     {"id": "2", "name": "NVIDIA GeForce RTX 4080"},
#     {"id": "3", "name": "NVIDIA GeForce RTX 3090"},
#     {"id": "4", "name": "AMD Radeon RX 7900 XTX"},
#     {"id": "5", "name": "NVIDIA A100 Tensor Core GPU"},
#     {"id": "6", "name": "NVIDIA A100 Tensor Core GPU"},
# ]

# allocated_gpus = {}
# next_policy_id = 1

# ----------------------------------------------------------------------


# # --- 모든 GPU 목록 조회 API ---
# @app.route('/api/sample/gpus', methods=['GET'])
# def get_all_gpus():
#     return jsonify(GPUS), 200

# # --- GPU 할당 정책 관련 API ---
# @app.route('/api/sample/allocation-policies', methods=['GET'])
# def get_all_allocation_policies():
#     policies_display = []
#     for policy_id, policy_data in allocated_gpus.items():
#         policy_display = policy_data.copy()
#         policy_display['createdAt'] = format_datetime_for_json(policy_display['createdAt'])
#         policy_display['expiredAt'] = format_datetime_for_json(policy_display['expiredAt'])
#         policies_display.append(policy_display)
#     policies_display.sort(key=lambda x: x['id'])
#     return jsonify(policies_display), 200

# @app.route('/api/sample/allocation-policies', methods=['POST'])
# def add_allocation_policy():
#     global next_policy_id
#     data = request.get_json()

#     if not data:
#         return jsonify({"message": "JSON 데이터가 필요합니다."}), 400

#     username = data.get('username')
#     gpu_id = data.get('gpuId') # resourceId 대신 gpuId
#     initial_activation = data.get('initialActivation', True)
#     expired_at_str = data.get('expiredAt')

#     if not all([username, gpu_id, expired_at_str]):
#         return jsonify({"message": "사용자명, GPU ID, 만료일은 필수입니다."}), 400

#     user = users.get(username)
#     if not user:
#         return jsonify({"message": "사용자를 찾을 수 없습니다."}), 404

#     # 유효한 GPU ID인지 확인
#     gpu_info = next((gpu for gpu in GPUS if gpu['id'] == gpu_id), None)
#     if not gpu_info:
#         return jsonify({"message": "유효하지 않은 GPU ID입니다."}), 404

#     try:
#         expired_at = datetime.fromisoformat(expired_at_str.replace('Z', '+00:00')).astimezone(timezone.utc)
#     except ValueError:
#         return jsonify({"message": "만료일 형식이 올바르지 않습니다. (ISO 8601)"}), 400

#     # 중복 할당 정책 확인 (같은 사용자에게 같은 GPU 할당 방지)
#     for policy in allocated_gpus.values():
#         if policy['username'] == username and policy['gpuId'] == gpu_id:
#             return jsonify({"message": "이미 해당 사용자에게 할당된 GPU입니다."}), 409

#     new_policy = {
#         "id": next_policy_id, # 정책 고유 ID
#         "username": username,
#         "gpuId": gpu_id,
#         "gpuName": gpu_info['name'], # GPU 모델명 추가
#         "initialActivation": initial_activation,
#         "createdAt": datetime.now(timezone.utc), # 할당 생성 시간
#         "expiredAt": expired_at,
#     }
#     allocated_gpus[next_policy_id] = new_policy
#     next_policy_id += 1

#     print(f"새로운 GPU 할당 정책 추가됨: {new_policy}")
#     response_policy = new_policy.copy()
#     response_policy['createdAt'] = format_datetime_for_json(response_policy['createdAt'])
#     response_policy['expiredAt'] = format_datetime_for_json(response_policy['expiredAt'])
#     return jsonify({"message": "GPU 할당 정책이 성공적으로 추가되었습니다.", "policy": response_policy}), 201

# # ----------------------------------------------------------------------

# def generate_dummy_allocation_policies(num_policies=5):
#     global next_policy_id
#     if not users or not GPUS: # 사용자나 GPU가 없으면 생성 안함
#         print("더미 정책을 생성할 사용자나 GPU가 없습니다.")
#         return

#     existing_allocations = set() # (username, gpu_id) 튜플 저장하여 중복 방지

#     for i in range(num_policies):
#         try:
#             # 랜덤 사용자 선택
#             username = random.choice(list(users.keys()))
#             user = users[username]

#             # 랜덤 GPU 선택
#             gpu_info = random.choice(GPUS)
#             gpu_id = gpu_info['id']

#             # 중복 체크
#             if (username, gpu_id) in existing_allocations:
#                 continue # 이미 존재하는 할당이면 다음으로

#             created_at = datetime.now(timezone.utc) - timedelta(days=random.randint(0, 30))
#             expired_at = datetime.now(timezone.utc) + timedelta(days=random.randint(30, 365))
#             initial_activation = random.choice([True, False])

#             new_policy = {
#                 "id": next_policy_id,
#                 "username": username,
#                 "gpuId": gpu_id,
#                 "gpuName": gpu_info['name'],
#                 "initialActivation": initial_activation,
#                 "createdAt": created_at,
#                 "expiredAt": expired_at,
#             }
#             allocated_gpus[next_policy_id] = new_policy
#             existing_allocations.add((username, gpu_id))
#             next_policy_id += 1
#         except IndexError: # users나 GPUS가 비어있을 경우 (드물지만)
#             break
#         except Exception as e:
#             print(f"더미 정책 생성 중 오류 발생: {e}")
#             break

#     print(f"{len(allocated_gpus)} 명의 더미 할당 정책이 생성되었습니다.")
#     print(f"다음 등록될 정책 ID: {next_policy_id}")

# generate_dummy_allocation_policies(10) # 더미 GPU 할당 정책 생성 (10개)
