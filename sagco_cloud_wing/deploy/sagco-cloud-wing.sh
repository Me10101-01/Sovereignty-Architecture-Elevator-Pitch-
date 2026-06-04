#!/bin/sh
# SAGCO-CLOUD-WING: brick → image → Cloud Run deploy
# Usage: ./sagco-cloud-wing.sh <brick> [job] [region]
# Example: ./sagco-cloud-wing.sh sagco_dojo c160201c europe-west1

BRICK="$1"
JOB="${2:-c160201c}"
REGION="${3:-europe-west1}"
DICT="$(dirname "$0")/../dictionary/images.txt"

IMG="$(grep "^$BRICK=" "$DICT" | cut -d= -f2-)"

if [ -z "$IMG" ]; then
  echo "BRICK_NOT_FOUND=$BRICK"
  echo "available:"
  grep -v '^#' "$DICT" | grep '=' | cut -d= -f1
  exit 1
fi

echo "SAGCO_CLOUD_WING_DEPLOY"
echo "BRICK=$BRICK"
echo "IMAGE=$IMG"
echo "JOB=$JOB"
echo "REGION=$REGION"

LOG="$(dirname "$0")/../logs/last_deploy.txt"
echo "BRICK=$BRICK"   > "$LOG"
echo "IMAGE=$IMG"    >> "$LOG"
echo "JOB=$JOB"      >> "$LOG"
echo "REGION=$REGION" >> "$LOG"
echo "TIMESTAMP=$(date -u +%Y%m%dT%H%M%SZ)" >> "$LOG"

gcloud run jobs update "$JOB" \
  --image "$IMG" \
  --region "$REGION"

EXIT=$?
if [ $EXIT -eq 0 ]; then
  echo "STATUS=SAGCO_CLOUD_WING_DEPLOYED"
  echo "NEXT: gcloud run jobs execute $JOB --region $REGION"
else
  echo "STATUS=SAGCO_CLOUD_WING_FAIL EXIT=$EXIT"
fi
exit $EXIT
