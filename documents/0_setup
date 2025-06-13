# 1. Setup Development Environment

## 1.1. 필수 준비 사항

### 1.1.1. nvm (Node Version Manager) 설치

참고 : https://github.com/nvm-sh/nvm

1. nvm 설치
    ```bash
    brew install nvm
    ```
2. `~/.zshrc`에 아래 내용 추가 (`~/.bash_profile`도 가능)
    ```bash
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
    ```
3. 설치 확인
    ```bash
    source ~/.zshrc && nvm --version
    ```

### 1.1.2. Node.js 설치

1. Node.js의 최신 LTS 버전 설치 (작성 기준 버전: `v22.16.0`)
    ```
    nvm install v22.16.0
     or 
    nvm install --lts
    ```
2. 설치한 버전을 기본값으로 설정 (선택사항)
    ```
    nvm alias default 20.12.2
    ```
3. 설치 확인
    ```
    node -v && npm -v
    ```

### 1.1.3 yarn 패키지 매니저 설치

1. yarn 설치
    ```
    npm install -g yarn
    ```
2. 설치 확인

    ```
    yarn -v
    ```


## 1.2 프로로젝트 개발 환경 구성 (Vuetify3 + Vite)

1. github 저장소 복제
    ```
    git clone https://github.com/jugangdae/gpu-board
    cd gpu-board
    ```
2. 패키지 설치
    ```
    yarn install
    ```
2. 개발용 서버 테스트 (빌드 포함)
    ```
    yarn dev
    ```
    참고: API 서버 환경 필수

## 1.3. 테스트용 API 서버 구성 (Python Flask) 

### 1.3.1. `venv` 가상환경 구성

1. 파이썬 가상환경 만들기
    ```
    cd gpu-board/backend
    python3 -m venv .venv
    ```
2. 파이썬 가상환경 활성화
    ```
    source .venv/bin/activate
    ```
### 1.3.2. API 서버 실행 (가상환경 활성화 후 진행)
1. 패키지 설치
    ```
    pip install -r requirements.txt
    ```
2. 실행
    ```
    python main.py
    ```

