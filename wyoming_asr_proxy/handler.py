# handler.py (полная версия с универсальными проверками)

import logging
import time
from typing import Set, Dict, Any

import numpy as np
from wyoming.asr import Transcribe, Transcript
from wyoming.audio import AudioChunk, AudioStart, AudioStop
from wyoming.event import Event
from wyoming.info import Describe, Info
from wyoming.server import AsyncEventHandler

from .verifier import MultiSpeakerVerifier

_LOGGER = logging.getLogger()

AUDIO_DTYPE = np.int16
INT16_MAX_VALUE = 32768.0

class STTProxyEventHandler(AsyncEventHandler):
    """Event handler for clients."""

    conversation_state: Dict[str, Any] | None = None

    def __init__(
        self,
        wyoming_info: Info,
        stt_client,
        cli_args,
        verifier: MultiSpeakerVerifier,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        self.wyoming_info_event = wyoming_info.event()
        self.stt_client = stt_client
        self.cli_args = cli_args
        self.verifier = verifier
        
        self.audio_buffer = bytearray()
        self.audio_rate = 16000

    async def handle_event(self, event: Event) -> bool:
        # Этот метод остается без изменений
        if AudioStart.is_type(event.type):
            self.audio_buffer.clear()
            start_event = AudioStart.from_event(event)
            self.audio_rate = start_event.rate
            await self.stt_client.write_event(event)
            return True

        if AudioChunk.is_type(event.type):
            chunk_event = AudioChunk.from_event(event)
            self.audio_buffer.extend(chunk_event.audio)
            await self.stt_client.write_event(event)
            return True

        if AudioStop.is_type(event.type):
            _LOGGER.debug("Audio stopped. Processing...")
            
            audio_array_int16 = np.frombuffer(self.audio_buffer, dtype=AUDIO_DTYPE).copy()
            audio_array_float32 = audio_array_int16.astype(np.float32) / INT16_MAX_VALUE
            self.audio_buffer.clear()
            
            # verifier.get_similarity_scores теперь вернет словарь с настоящими именами,
            # например: {"Митя": 0.8, "Аня": 0.3}
            similarity_scores = self.verifier.get_similarity_scores(
                audio_array_float32, sample_rate=self.audio_rate
            )
            if similarity_scores:
                formatted_scores = ", ".join([f"{name}: {score:.3f}" for name, score in similarity_scores.items()])
                _LOGGER.info(f"Speaker similarity scores: [{formatted_scores}]")
            
            transcript_text = await self._get_transcript(event)
            if transcript_text is None:
                return True

            tag_text = self._get_tag_text(transcript_text, similarity_scores)

            final_text = transcript_text + tag_text
            if tag_text:
                _LOGGER.info(f"Speaker identified. Original: '{transcript_text}', Tagged: '{tag_text}'")
            else:
                _LOGGER.info(f"Transcript received: '{transcript_text}'")

            await self.write_event(Transcript(text=final_text).event())
            _LOGGER.debug("Completed request")
            await self.stt_client.disconnect()
            return False

        if Transcribe.is_type(event.type):
            await self.stt_client.connect()
            await self.stt_client.write_event(event)
            _LOGGER.debug("Transcription session started.")
            return True

        if Describe.is_type(event.type):
            async with self.stt_client:
                await self.stt_client.write_event(event)
                stt_info_event = await self.stt_client.read_event()

            if stt_info_event and Info.is_type(stt_info_event.type):
                stt_info = Info.from_event(stt_info_event)
                if stt_info.asr:
                    self.wyoming_info_event.data['asr'][0]['models'][0] = stt_info.asr[0].models[0].to_dict()
                    self.wyoming_info_event.data['asr'][0]['models'][0]['name'] += " (with identification)"

            await self.write_event(self.wyoming_info_event)
            _LOGGER.debug("Sent info")
            return True

        return True

    def _get_tag_text(self, text: str, scores: dict) -> str:
        """Решает, нужно ли добавлять тег, и обновляет состояние беседы."""
        
        now = time.monotonic()

        if STTProxyEventHandler.conversation_state and (now - STTProxyEventHandler.conversation_state["last_activity_time"] > self.cli_args.tag_cooldown):
            _LOGGER.info("Conversation window timed out. Resetting.")
            STTProxyEventHandler.conversation_state = None

        if STTProxyEventHandler.conversation_state is None:
            STTProxyEventHandler.conversation_state = {
                "last_activity_time": now,
                "tagged_speakers": set()
            }
            _LOGGER.info("New conversation window started.")
        else:
            STTProxyEventHandler.conversation_state["last_activity_time"] = now
            _LOGGER.debug("Conversation window extended.")
            
        if not scores:
            return ""
        
        best_speaker = max(scores, key=scores.get)
        best_similarity = scores[best_speaker]

        conditions_met = (
            best_similarity > self.cli_args.similarity_threshold and
            len(text.split()) >= self.cli_args.min_words
        )

        if not conditions_met:
            return ""

        if best_speaker in STTProxyEventHandler.conversation_state["tagged_speakers"]:
            _LOGGER.info(f"Speaker '{best_speaker}' already tagged in this conversation window. Skipping tag.")
            return ""
            
        STTProxyEventHandler.conversation_state["tagged_speakers"].add(best_speaker)

        # --- ИЗМЕНЕНИЕ: Блок заменен на универсальную f-строку ---
        # best_speaker теперь содержит имя, заданное в командной строке (например, "Митя" или "Аня").
        # Мы можем сформировать тег динамически.
        return f" [it's {best_speaker} voice]"

    async def _get_transcript(self, stop_event: AudioStop) -> str | None:
        """Отправляет аудио в STT и возвращает текст."""
        await self.stt_client.write_event(stop_event)
        while True:
            return_event = await self.stt_client.read_event()
            if return_event is None:
                _LOGGER.warning("Upstream STT service closed connection unexpectedly.")
                return None
            
            if Transcript.is_type(return_event.type):
                return Transcript.from_event(return_event).text