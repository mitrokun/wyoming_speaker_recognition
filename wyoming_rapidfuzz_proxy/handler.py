import logging
from wyoming.asr import Transcribe, Transcript
from wyoming.audio import AudioChunk, AudioStop, AudioStart
from wyoming.event import Event
from wyoming.info import Describe, Info
from wyoming.server import AsyncEventHandler
from wyoming.asr import Transcribe, Transcript
from wyoming.audio import AudioStop
from wyoming.info import Describe, Info
from wyoming.event import Event
from .sentences import load_sentences_for_language, correct_sentence

_LOGGER = logging.getLogger()

class STTProxyEventHandler(AsyncEventHandler):
    """Event handler for clients."""

    def __init__(
        self,
        wyoming_info: Info,
        stt_clientt,
        cli_args,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        self.wyoming_info_event = wyoming_info.event()
        self.stt_clientt = stt_clientt
        self.cli_args = cli_args

    async def handle_event(self, event: Event) -> bool:
        if AudioChunk.is_type(event.type):
            await self.stt_clientt.write_event(event)
            return True

        if AudioStart.is_type(event.type):
            await self.stt_clientt.write_event(event)
            return True

        if AudioStop.is_type(event.type):
            _LOGGER.debug("Audio stopped.")
            await self.stt_clientt.write_event(event)
            while True:
                return_event = await self.stt_clientt.read_event()
                if return_event is None:
                    _LOGGER.info("Unexpected empty event")
                    return True
                if Transcript.is_type(return_event.type):
                    text = return_event.data["text"].lower().removesuffix(".")
                    original_text = text

                    if self.cli_args.correction_threshold is not None:
                        text = self.fix_transcript(original_text)
                        if text != original_text:
                            _LOGGER.info(
                                "Original: " + original_text + " Corrected: " + text
                            )
                    _LOGGER.info("Sent: %s", text)
                    await self.write_event(Transcript(text=text).event())
                    _LOGGER.debug("Completed request")
                    await self.stt_clientt.__aexit__(None, None, None)
                    return False

        if Transcribe.is_type(event.type):
            await self.stt_clientt.__aenter__()
            await self.stt_clientt.write_event(event)
            transcribe = Transcribe.from_event(event)
            _LOGGER.debug("Language set to %s", transcribe.language)
            return True

        if Describe.is_type(event.type):
            await self.stt_clientt.__aenter__()
            await self.stt_clientt.write_event(event)
            while True:
                return_event = await self.stt_clientt.read_event()
                if Info.is_type(return_event.type):
                    return_event.data["asr"][0]["name"] = (
                        return_event.data["asr"][0]["name"] + " with RapidFuzz"
                    )
                    await self.write_event(return_event)
                    _LOGGER.debug("Sent info")
                    await self.stt_clientt.__aexit__(None, None, None)
                    return True
        return True

    def fix_transcript(self, text: str) -> str:
        """Corrects a transcript using user-provided sentences."""
        assert self.cli_args.language, "Language not set"
        lang_config = load_sentences_for_language(
            self.cli_args.data_dir,
            self.cli_args.language,
            self.cli_args.data_dir,
        )

        if self.cli_args.allow_unknown and self._has_unknown(text):
            if lang_config is not None:
                return lang_config.unknown_text or ""

            return ""

        if lang_config is None:
            # Can't fix
            return text

        return correct_sentence(
            text, lang_config, score_cutoff=self.cli_args.correction_threshold
        )

    def _has_unknown(self, text: str) -> bool:
        """Return true if text contains unknown token."""
        unk_token = UNK_FOR_MODEL.get(self.model_name, _DEFAULT_UNK)
        return (text == unk_token) or (unk_token in text.split())