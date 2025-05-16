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

# Volumes
"By default, Wyoming RapidFuzz Proxy uses a single default mount point to access the statement definition file."

| Path | Description | Example |
|-----------|-----------|-----------|
| /data| This directory must contain a file with the statements that will be used for the correction process. The file should be named <language>.yaml. You can create your own, use an existing file compatible with Wyoming Vosk, or use one of the example files available in the Wyoming Vosk repository (https://github.com/rhasspy/wyoming-vosk/tree/master/examples). | ./sentences |


# Docker-compose environment variables

| Variable | Description | Example |
|-----------|-----------|-----------|
| URI| URL that defines the host and listening port of the proxy. The port you set in this parameter is the port you must use in Home Assistant and expose in the container if you are using bridge mode networking.| tcp://0.0.0.0:10310|
| STT_URI| Connection URI to the Wyoming Speech to Text service you want to use.| tcp://192.168.1.100:10300|
| CORRECTION_THRESHOLD | Sets the maximum Levenshtein distance allowed between an audio transcription and its closest correction. If the difference is within the threshold, the correction is applied; otherwise, the original sentence is kept. Higher thresholds allow more corrections but may alter open-ended phrases. A value of 0 disables all corrections. See **c** for more info | 15|
| LANGUAGE| Language code of the language you want to use. There must be a sentence definition file in the /data folder named “[language].yaml” (e.g., “/data/en.yaml”). See **Volumes** for more info| en|
| LIMIT_SENTENCES| Refer to: https://github.com/rhasspy/wyoming-vosk| FALSE|
| ALLOW_UNKNOWN | Refer to: https://github.com/rhasspy/wyoming-vosk | FALSE|
| DEBUG_LOGGING| Print debug log on container console output| FALSE|

# Understanding CORRECTION_THRESHOLD
This directory must contain a file with the statements that will be used for the correction process. The file should be named <language>.yaml. You can create your own, use an existing file compatible with Wyoming Vosk, or use one of the example files available in the Wyoming Vosk repository (https://github.com/rhasspy/wyoming-vosk/tree/master/examples).

The correction process uses the Levenshtein distance between the transcribed phrase from a voice command and the predefined phrases in the sentecnes file (E.g: In the en.yaml).
Simply put, the Levenshtein distance between two texts is the minimum number of single-character operations (insertions, deletions, or substitutions) needed to transform one text into the other.
If the two texts are identical, the distance is zero. Otherwise, the more different the texts are, the greater the distance will be.

The environment variable CORRECTION_THRESHOLD determines the maximum allowable distance between two phrases for the sentence correction to be applied.
If this value is set to 0, sentence correction will not be applied at all. On the other hand, if the value is too high, all phrases will be corrected, blocking any command that is not in the list of predefined phrases.

As a recommendation, this parameter should be set to a value that allows at most one or two full words to be changed in a sentence. This should be based on the typical length of area or entity names used in the phrases.
