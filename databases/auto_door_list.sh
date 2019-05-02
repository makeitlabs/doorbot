#!/bin/bash
RESOURCE=frontdoor
AUTHHOST=auth.makeitlabs.com
URL=https://${AUTHHOST}/authit/api/v1/resources/${RESOURCE}/acl
PWFILE=/home/pi/doorbot/databases/curlpw
OUTFILE=/home/pi/doorbot/databases/rfid/acl.json

curl --silent --fail --output ${OUTFILE} --netrc-file ${PWFILE} ${URL}

