# kafka-connect-manager

- kafka connect에서 connector를 생성, 삭제, 관리하기 위한 라이브러리
- 실사용시 편의성을 고려하여 조금씩 개선해나간다.
- 커넥터 설정은 yaml로 기술하고, 배포시에 json으로 변환
  - 다수 커넥터 배포시 공통부분 기술이 필요
  - 세부옵션에 대한 주석 메모 필요

## tree

```sh
.
├── LICENSE
├── README.md
├── python-post/  # Python 및 HTTP POST 기반 커넥터 등록 앱(legacy)
└── shell-put/    # Shell 및 HTTP PUT 기반 커넥터 등록 앱(권장)
    ├── config/
    ├── apply-connectors-debian.sh  # 커넥터 등록기 (데비안 패키지로만 의존성 구성)
    ├── apply-connectors.sh         # 커넥터 등록기 (go-yq로만 의존성 구성)
    ├── plan-connectors.sh          # 커넥터 설정 체크 및 스크립트 생성
    └── yq_linux_amd64.tar.gz
```

## Shell-put 

- Python앱 대신 Shell스크립트 단일파일로 전환
  - 의존성 감소, 쉬운 배포 난이도(컨테이너/온프레미스폐쇄망 등)
- POST 대신 PUT 사용
  - 운영관점에서 PUT이 나음 (등록 및 업데이트)
  - 커넥터 config 기술 방식도 간단해짐

### How to Use

```sh
cd shell-put

# 커넥터 등록or 업데이트
apply-conenctors.sh config/sample.yaml

# 커넥터 config 검증 및 등록용 스크립트 출력
plan-connectors.sh config/sample.yaml

# 커넥터 config json만 출력
plan-connectors.sh config/sample.yaml | grep -v EOF
```

---

## (참고)핵심 의존성 yq (jq와 비슷한 yaml 처리 도구)

```sh
# Go-yq
sudo snap install yq
wget https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 -O /usr/local/bin/yq &&\
    chmod +x /usr/local/bin/yq
```

- 동일한 이름의 yq가 있는데 Go 기반 yq를 사용한다. python의 yq와 헷갈리지 않도록 주의

### go-yq (mikefarah/yq)

- `단일 binary로 배포가능`
- Go 기반의 yaml 도구라 쿠버네티스 생태계에서 자주 쓰이며, 점유율도 높음
- 그냥 `yq라 칭하면 Go-yq임(사실상 표준)`
- python-yq보다 빠르고, 기능이 훨씬 더 많음

### python-yq (kislyuk/yq)

- jq 포함 및 문법 완전 호환으로 기존 jq사용자에겐 매우 쉬움
- 전반적인 기능과 옵션 구성이 심플해서 실무 활용 시 편함
- 옵션없이 단순실행 시 YAML을 JSON으로 변환
  - 이후 과정은 C 기반의 빠른 jq로 처리 가능
  - 데이터 입출력만 python-yq를 써도 훌륭함
- 단 json변환없이 yaml로만 데이터를 다룰시, python기반이라 속도저하 심함
- python, jq 등 의존성이 많아서, 컨테이너/온프레미스 배포시 제약 가능성
