#!/bin/bash

URL='https://api.rag22reboot.ece17.rocks/admin_api'
TOKEN=''

curl -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"type":"sync_sms_api","data":{}}' $URL
