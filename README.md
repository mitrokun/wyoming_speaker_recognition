# Wyoming speaker recognition
This project integrates into the existing STT pipeline, creates embeddings based on samples of your voices, and compares them with your voice for each request ( [Resemblyzer library](https://github.com/resemble-ai/Resemblyzer ) is used). If the condition is met, the system tags the recognized text with '[it's Alice voice]' (using your name) for LLM context. This action is performed once per "session." Since Wyoming does not transmit a conversation ID, we reset the pointer if 5 minutes have passed since the last request (the default value for AssistSatellite).

There is also a condition for a minimum of 5 words (configurable) in a phrase to allow the execution of regular commands.

It’s worth noting that this is not a serious project but a proof of concept.

## Install
```
git clone https://github.com/mitrokun/wyoming_speaker_recognition.git
cd wyoming_speaker_recognition
python3 -m venv venv
source venv/bin/activate
pip install resemblyzer
```
or if you don't need extra dependencies for nvidia
```
pip install torch==2.3.1+cpu torchvision==0.18.1+cpu torchaudio==2.3.1+cpu -f https://download.pytorch.org/whl/torch_stable.html
pip install setuptools wyoming typing
pip install resemblyzer --no-deps
pip install webrtcvad librosa
deactivate
chmod +x run
```
## Run

I recommend recording a 10-15 second sample using HA debug mode. Place the files in the sample folder. Configure the run script and launch it. Creating embeddings may take some time on low-end hardware, but this is a one-time operation.
```
./run

```
