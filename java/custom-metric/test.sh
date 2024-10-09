#!/bin/bash


export from=$(( $(date +%s) - 600 ))  # 10 minutes ago
export to="$(date +%s)"
export query="count:rey.custom.java\{*\}.as_count()"

result=$(curl -X GET "https://api.datadoghq.com/api/v1/query?from=${from}&to=${to}&query=${query}" \
-H "Accept: application/json" \
-H "DD-API-KEY: ${DD_API_KEY}" \
-H "DD-APPLICATION-KEY: ${DD_APP_KEY}" 2>/dev/null)

python -c "
import json
data = json.loads('''$result''')
total = 0
if len(data['series']) > 0:
    for point in data['series'][0]['pointlist']:
        total += point[1]
print(int(total))
"
