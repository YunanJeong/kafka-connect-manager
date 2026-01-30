#!/bin/bash

# [Requirement]
# sudo snap install yq (Or binary from https://github.com/mikefarah/yq, Go-based)
# Do NOT use `apt install yq` (different tool, python-based)

FILE=$1
API="http://localhost:8083/connectors"

# 인자없으면 종료
if [ ! -f "$FILE" ]; then echo "Usage: $0 <file>"; exit 1; fi

# yaml 읽어서 json으로 저장, 이후에도 가급적 yq binary 단독파일로 모든 것을 해결
COMMON=$(yq -o=json '.common' "$FILE")
CONNECTORS=$(yq -o=json '.connectors[]' "$FILE")

# 병합
# PAYLOADS=$(echo "$CONNECTORS" | jq -c --argjson common "$COMMON" '$common * .' | envsubst)
PAYLOADS=$( yq eval-all -p=json -o=json -I=0 ' select(fi == 0) * select(fi == 1)' <(echo "$COMMON") <(echo "$CONNECTORS") )
PAYLOADS=$(echo "$PAYLOADS" | envsubst)

# 각 커넥터별로 PUT 전송
while read -r PAYLOAD; do

  NAME=$(echo "$PAYLOAD" | yq -r '.name')
  
  # 테스트 출력 (필요시에만 주석해제. 보안위험있으므로 운영시 출력금지)
  # echo "$PAYLOAD" | yq -o=json

  # 실제 전송 
  echo "$PAYLOAD" | curl -s -X PUT -H "Content-Type: application/json" -d @- "$API/$NAME/config"
  
done <<< "$PAYLOADS"

# ---
# Go-based yq Options Explanation
### yq Core Options & Operators
# -p=json / --input-format=json : Input포맷을 명시적으로 지정. 입력 데이터가 JSON임을 강제하여 파싱 에러(document start 등) 방지
# -o=j / -o=json : Output JSON. 결과를 JSON 형식으로 출력. API 전송 및 연동 시 필수
# -r / --raw-output : Raw string. 문자열 출력 시 감싸는 따옴표(")를 제거하여 순수 값만 추출
# -n / --null-input : Null input. 파일을 읽지 않고 연산 수행하거나 변수 기반의 새 객체 생성 시 사용
# -P / --prettyPrint : Pretty print. 가독성을 위해 출력 형식을 정렬 (YAML 기본값)
# -i / --inplace : In-place update. 결과를 표준 출력으로 내보내지 않고 원본 파일을 즉시 수정
# -v / --verbose : Debug mode. 실행 과정을 상세히 출력하여 쿼리 오류 추적 시 사용
# -I=N / --indent=N : Indentation level. 출력 시 들여쓰기 수준을 지정 (default 2)
  # -I=0 : Compact하게 출력(공백 및 줄바꿈 없이 출력).=> Json 대상으로 사용시 jq -c 와 같은 효과. 단일 json을 1줄로 만듦. 
# eval-all / ea : Slurp mode. 여러 개의 입력 파일을 모두 메모리에 로드하여 병합(Merge) 등의 연산 수행
  # yq 기본동작(eval)은 데이터를 문서 단위로 개별처리하고,
  # eval-all은 여러 문서를 한꺼번에 다룰 때 쓴다.
  # 단일 문서 = 단일 yaml, 단일 json 을 의미
  # 여러 문서(---로 구분된 yaml파일, json라인이 나열된 단일파일 등)를 한 번에 처리하기 위해 eval-all 옵션 사용
# envsubst : Operator. 쉘 환경변수를 JSON/YAML 내부의 `${VAR}` 위치에 직접 주입 
# ---