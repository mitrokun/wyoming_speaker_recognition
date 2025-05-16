flags=()

if [ "${DEBUG_LOGGING}" == "TRUE" ]; then
    flags+=('--debug')
fi

if [ "${CORRECTION_THRESHOLD}" == "TRUE" ]; then
    flags+=('--correction-threshold')
fi

if [ "${ALLOW_UNKNOWN}" == "TRUE" ]; then
    flags+=('--allow-unknown')
fi

echo STT_URI                =   ${STT_URI}    
echo URI                    =   ${URI}
echo CORRECTION_THRESHOLD   =   ${CORRECT_SENTENCES}
echo LANGUAGE               =   ${LANGUAGE}
echo DEBUG_LOGGING          =   ${DEBUG_LOGGING}
echo LIMIT_SENTENCES        =   ${LIMIT_SENTENCES}
echo ALLOW_UNKNOWN          =   ${ALLOW_UNKNOWN}

cd /usr/wyoming_rapidfuzz_proxy

echo flags = ${flags[@]}
python3 -m wyoming_rapidfuzz_proxy \
    --stt-uri ${STT_URI} \
    --uri ${URI} \
    --data-dir /data \
    --correction-threshold $CORRECTION_THRESHOLD \
    --language $LANGUAGE \
    ${flags[@]}
