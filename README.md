# Prepare(Mac OS 기준)

## nvm 설치
```
brew install nvm
```
## node 설치
```
 nvm install --lts
```
확인 : `nvm version` -> v22.16.0
## yarn 설치
```
npm install -g yarn
```

# Setup

## Clone repo

```
git clone https://github.com/jugangdae/gpu-board
```

## Install pacakges
```
cd gpu-board
npm i
```

## Test

```
yarn dev
```

# TODO

## 역할 분담
1. 대시보드 (metrics/KPI/실시간 모니터링/맞춤형 대시보드)
2. 자원 관리 (GPU 자원 현황, 회수, 할당, 정책 등)
3. 사용자 관리 + 보고서 (계정관리/권한, 통계보고 화면까지)


## PPT 기준
- 대시보드: 
    - 주요 정보의 시각적 표현: 전체 자원 활용률 (CPU, GPU, 메모리), 자원 유휴 시간 및 개별 사용자별 자원 사용량과 같은 주요 성능 지표 (KPI) 및 시스템 지표를 시각적으로 표시
    - 실시간 모니터링: GPU 클러스터 자원 및 시스템 자체의 현재 상태 및 건강 상태를 추적하기 위한 실시간 모니터링 기능을 제공
    - 맞춤형 대시보드: 관리자가 보고 싶은 지표와 정보를 선택하여 대시보드 보기를 사용자 지정할 수 있는 기능을 탐색

- 자원 관리: 
    - 할당된 자원 및 사용자 정보 보기: 현재 할당된 모든 GPU 자원과 이를 할당받은 사용자를 명확하게 볼 수 있는 기능을 관리자에게 제공
    - 자원 회수 및 사용 기간 조정: 관리자가 사용자에게 할당된 자원을 수동으로 회수 (취소)하고 기존 할당에 대한 사용 기간을 조정할 수 있는 기능 
    - 자원 할당 정책 구성: 관리자가 최대 사용 기간 및 사용자별 할당 제한과 같은 자원 할당 정책을 구성하고 관리

- 사용자 관리:
    - 사용자 계정 관리: 관리자가 시스템에서 사용자 계정을 생성, 수정 및 삭제할 수 있는 기능 제공  
    - 사용자 역할 및 권한 관리: 관리자, 일반 사용자 등 사용자 역할을 관리하고 각 역할에 특정 권한을 할당하는 시스템

- 보고서: 
    - 자원 사용량 보고서: 총 사용량, 특정 사용자별 사용량 및 시간별 사용량과 같은 자원 사용 패턴에 대한 보고서를 생성
    - 유휴 시간 보고서: 자원이 유휴 상태였던 시간에 대한 보고서를 제공하여 잠재적인 비효율성을 식별

# Note
1. `src/pages`에 각 페이지에 해당하는 기능 개발
2. `src/components`에 필요한 부품 만들어서 재사용 가능

---
```
yarn create vuetify

✔ Project name: gpu-board
✔ Which preset would you like to install?: Default (Adds routing, ESLint & SASS variables)
✔ Use TypeScript?: No
✔ Would you like to install dependencies with yarn, npm, pnpm, or bun?: yarn
✔ Install Dependencies?: Yes
```