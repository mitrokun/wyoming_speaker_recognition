# Wyoming RapidFuzz Proxy
A wyoming proxy to add Vosk Rapid Fuzz sentence correction to any wyoming Speech-To-Text service

# Thanks to
* This project is mainly a wrapper around the sentence correction using RapidFuzz from Wyoming Vosk (https://github.com/rhasspy/wyoming-vosk).The correction code was written by synesthesiam. Thanks to him.
* I’m not a developer, so I’ve taken parts and pieces to start this project. One of these is the scripts to containerize Vosk from https://github.com/dekiesel/wyoming-vosk-standalone.

# Prerequisites
* A working Wyoming Speech to Text like https://github.com/rhasspy/wyoming-faster-whisper or https://github.com/hugobloem/wyoming-microsoft-stt
* docker
* docker compose (or another way of starting the container)

# How to use
* clone the repo `git clone https://github.com/Cheerpipe/wyoming_rapidfuzz_proxy`
* change into the repo: `cd wyoming_rapidfuzz_proxy`
* build the container: `bash scripts/build.sh`
* Edit `docker-compose.yaml`
* Create a file with the sentences that will be used for correction. You can start with one of the examples from the Vosk repository (https://github.com/rhasspy/wyoming-vosk/tree/master/examples). Or if you are already a Vosk user, directly use your current sentence file.
* run the container: `docker compose up` or `docker compose up -d` for detached execution.

# Docker-compose environment variables

| Variable | Description | Example |
|-----------|-----------|-----------|
| URI| URL that defines the host and listening port of the proxy. The port you set in this parameter is the port you must use in Home Assistant and expose in the container if you are using bridge mode networking.| tcp://0.0.0.0:10310|
| STT_URI| Connection URI to the Wyoming Speech to Text service you want to use.| tcp://192.168.1.100:10300|
| CORRECTION_THRESHOLD | Sets the maximum Levenshtein distance allowed between an audio transcription and its closest correction. If the difference is within the threshold, the correction is applied; otherwise, the original sentence is kept. Higher thresholds allow more corrections but may alter open-ended phrases. A value of 0 disables all corrections. See **Understanding CORRECTION_THRESHOLD** for more info | 15|
| LANGUAGE| Language code of the language you want to use. There must be a sentence definition file in the /data folder named “[language].yaml” (e.g., “/data/en.yaml”). See **Volumes** for more info| en|
| LIMIT_SENTENCES| Refer to: https://github.com/rhasspy/wyoming-vosk| FALSE|
| ALLOW_UNKNOWN | Refer to: https://github.com/rhasspy/wyoming-vosk | FALSE|
| DEBUG_LOGGING| Print debug log on container console output| FALSE|
