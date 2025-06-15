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
url : http://localhost:8000/api/chartjs/multi?start=20250101&end=20250330
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
url : http://localhost:8000/api/chartjs/single?start=20250101&end=20250330
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
