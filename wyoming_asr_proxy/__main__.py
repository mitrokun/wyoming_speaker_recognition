# __main__.py (полная обновленная версия)

import argparse
import asyncio
import logging
from functools import partial

from wyoming.client import AsyncClient
from wyoming.info import AsrModel, AsrProgram, Attribution, Info
from wyoming.server import AsyncServer

from .handler import STTProxyEventHandler
from .verifier import MultiSpeakerVerifier

_LOGGER = logging.getLogger()

async def main() -> None:
    """Main entry point."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--uri", default="tcp://0.0.0.0:10301", help="unix:// or tcp://"
    )
    parser.add_argument(
        "--stt-uri", default="tcp://127.0.0.1:10300", help="unix:// or tcp://"
    )
    
    parser.add_argument(
        "--reference-audio-person1",
        required=True,
        help="Path to the reference .wav file for Person 1.",
    )
    parser.add_argument(
        "--reference-audio-person2",
        required=True,
        help="Path to the reference .wav file for Person 2.",
    )

    parser.add_argument(
        "--name-person1",
        required=True,
        help="Name for Person 1 (e.g., 'Alice').",
    )
    parser.add_argument(
        "--name-person2",
        required=True,
        help="Name for Person 2 (e.g., 'Bob').",
    )
    
    parser.add_argument(
        "--similarity-threshold",
        type=float,
        default=0.75,
        help="Similarity threshold (0.0 to 1.0) to identify the speaker. (Default: 0.75)",
    )
    parser.add_argument(
        "--min-words",
        type=int,
        default=5,
        help="Minimum number of words in transcript to trigger speaker tagging. (Default: 5)",
    )
    parser.add_argument(
        "--tag-cooldown",
        type=int,
        default=300,
        help="Cooldown in seconds to reset the conversation window. (Default: 300)",
    )
    parser.add_argument("--debug", action="store_true", help="Log DEBUG messages")
    parser.add_argument(
        "--log-format", default=logging.BASIC_FORMAT, help="Format for log messages"
    )

    cli_args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if cli_args.debug else logging.INFO,
        format=cli_args.log_format,
    )
    _LOGGER.debug(cli_args)

    wyoming_info = Info(
        asr=[
            AsrProgram(
                name="STT Proxy with Speaker Identification",
                description="A speech recognition proxy that adds speaker identification to any Wyoming STT",
                attribution=Attribution(
                    name="Felipe Urzúa & AI Assistant",
                    url="https://github.com/Felipe-Urzua/wyoming_asr_proxy",
                ),
                installed=True,
                version="1.3.0", # Версия обновлена
                models=[
                    AsrModel(
                        name="Downstream STT",
                        description="The STT service this proxy forwards to",
                        attribution=Attribution(name="Unknown", url="#"),
                        installed=True,
                        languages=[], 
                        version="unknown",
                    )
                ],
            )
        ],
    )

    reference_audios = {
        cli_args.name_person1: cli_args.reference_audio_person1,
        cli_args.name_person2: cli_args.reference_audio_person2,
    }

    try:
        verifier = MultiSpeakerVerifier(reference_audios)
    except Exception as e:
        _LOGGER.critical(f"Failed to initialize voice verifier: {e}")
        return

    stt_client = AsyncClient.from_uri(cli_args.stt_uri)
    server = AsyncServer.from_uri(cli_args.uri)

    _LOGGER.info("Ready")

    try:
        await server.run(
            partial(STTProxyEventHandler, wyoming_info, stt_client, cli_args, verifier)
        )
    except KeyboardInterrupt:
        pass
    
    _LOGGER.info("Terminating")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
