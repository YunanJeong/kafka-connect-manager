#!/bin/bash
FILE=$1
API="http://localhost:8083/connectors"

if [ ! -f "$FILE" ]; then echo "Usage: ./apply.sh <file>"; exit 1; fi

yq '.connectors[]' "$FILE" -c | while read -r item; do
  NAME=$(echo "$item" | yq '.name')
  # common 섹션과 현재 항목을 병합하여 JSON 생성
  PAYLOAD=$(yq "(.common * $item) | @json" "$FILE")

  # [방법 1] 테스트 출력용 (필요할 때 주석 해제)
  echo "[DEBUG]\n $NAME: $PAYLOAD"

  # [방법 2] 실제 반영용 (필요할 때 주석 해제)
  # echo "$PAYLOAD" | curl -s -X PUT -H "Content-Type: application/json" -d @- "$API/$NAME/config" | jq -c '.name'
done
