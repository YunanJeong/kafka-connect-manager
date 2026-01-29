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

