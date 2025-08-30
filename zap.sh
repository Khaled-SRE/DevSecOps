#!/bin/bash

TARGET_URL="${1:-https://admin.dev.beaconconnect.app}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_DIR="./reports/${TIMESTAMP}"

mkdir -p ${REPORT_DIR}

echo "Starting comprehensive OWASP ZAP scan for ${TARGET_URL}"

docker pull zaproxy/zap-stable:latest

# Run baseline scan (for comparison/debugging if needed)
echo "[1/3] Running baseline scan..."
docker run --rm -v $(pwd):/zap/wrk/:rw -t zaproxy/zap-stable:latest \
    zap-baseline.py -t ${TARGET_URL} \
    -x ${REPORT_DIR}/baseline_report.xml \
    -J ${REPORT_DIR}/baseline_report.json \
    -a -j -T 60

# Run comprehensive full scan (includes baseline + more)
echo "[2/3] Running comprehensive vulnerability scan..."
docker run --rm -v $(pwd):/zap/wrk/:rw -t zaproxy/zap-stable:latest \
    zap-full-scan.py -t ${TARGET_URL} \
    -x ${REPORT_DIR}/full_scan_report.xml \
    -J ${REPORT_DIR}/full_scan_report.json \
    -T 120

# Upload ONLY the comprehensive full scan to avoid duplicates
echo "[3/3] Uploading comprehensive scan results to DefectDojo..."
if [ -z "${DEFECT_DOJO_API_TOKEN}" ]; then
    echo "ERROR: Set DEFECT_DOJO_API_TOKEN first"
    exit 1
fi

python3 upload_to_defectdojo.py "${REPORT_DIR}" "${TARGET_URL}"

echo ""
echo "✅ Comprehensive DAST scan complete - no duplicate findings!"
echo "📊 Full scan provides complete vulnerability coverage"
echo "🔗 DefectDojo Dashboard: http://localhost:8080/dashboard"
 
