#!/bin/bash

# [Requirement]
# sudo apt install jq yq gettext curl
# yq is python based 

FILE=$1
API="http://localhost:8083/connectors"

# 인자없으면 종료
if [ ! -f "$FILE" ]; then echo "Usage: $0 <file>"; exit 1; fi

# 최초 yaml을 읽을 때만 yq 사용. 이후 json 처리
COMMON=$(yq '.common' "$FILE")
CONNECTORS=$(yq '.connectors[]' "$FILE")

# 병합
PAYLOADS=$(echo "$CONNECTORS" | jq -c --argjson common "$COMMON" '$common * .' | envsubst)
# PAYLOADS=$( yq eval-all -p=json -o=json -I=0 ' select(fi == 0) * select(fi == 1)' <(echo "$COMMON") <(echo "$CONNECTORS") )
PAYLOADS=$(echo "$PAYLOADS" | envsubst)

# 각 커넥터별로 PUT 전송
while read -r PAYLOAD; do

  NAME=$(echo "$PAYLOAD" | yq -r '.name')
  
  # 테스트 출력 (필요시에만 주석해제. 보안위험있으므로 운영시 출력금지)
  echo "$PAYLOAD" | jq

  # 실제 전송 
  # echo "$PAYLOAD" | curl -s -X PUT -H "Content-Type: application/json" -d @- "$API/$NAME/config"
  
done <<< "$PAYLOADS"

# ---
# yq Options Explanation
### yq Core Options & Operators
# -p=json / --input-format=json : Input JSON. 입력 데이터가 JSON임을 강제하여 파싱 에러(document start 등) 방지 [1]
# -o=j / -o=json : Output JSON. 결과를 JSON 형식으로 출력. API 전송 및 연동 시 필수 [2]
# -I=0 / --indent=0 : Compact Output. 들여쓰기를 없애 한 줄로 출력 (jq의 -c와 동일). 쉘 루프 처리 시 유용
# -r / --raw-output : Raw string. 문자열 출력 시 감싸는 따옴표(")를 제거하여 순수 값만 추출
# -n / --null-input : Null input. 파일을 읽지 않고 연산 수행하거나 변수 기반의 새 객체 생성 시 사용
# -P / --prettyPrint : Pretty print. 가독성을 위해 출력 형식을 정렬 (YAML 기본값)
# -i / --inplace : In-place update. 결과를 표준 출력으로 내보내지 않고 원본 파일을 즉시 수정
# -v / --verbose : Debug mode. 실행 과정을 상세히 출력하여 쿼리 오류 추적 시 사용
# eval-all / ea : Slurp mode. 여러 개의 입력 파일을 모두 메모리에 로드하여 병합(Merge) 등의 연산 수행 
# envsubst : Operator. 쉘 환경변수를 JSON/YAML 내부의 `${VAR}` 위치에 직접 주입 
# ---