# verifier.py (полная обновленная версия)

import os
from pathlib import Path
from typing import Dict

import numpy as np
from resemblyzer import VoiceEncoder, preprocess_wav

class MultiSpeakerVerifier:
    """
    Класс для верификации голоса нескольких спикеров.
    """
    def __init__(self, reference_audios: Dict[str, str]):
        """
        Инициализирует верификатор, создавая или загружая эталонные эмбеддинги.

        :param reference_audios: Словарь, где ключ - имя спикера, а значение - путь к его эталонному WAV файлу.
        """
        if not reference_audios:
            raise ValueError("Словарь с эталонными аудио не может быть пустым.")

        self.encoder = VoiceEncoder()
        self.reference_embeddings: Dict[str, np.ndarray] = {}

        for speaker_name, ref_audio_path in reference_audios.items():
            print(f"--- Инициализация спикера: {speaker_name} ---")
            
            ref_path = Path(ref_audio_path)
            embedding_path = ref_path.parent / f"{ref_path.stem}_embedding.npy"

            if os.path.exists(embedding_path):
                print(f"Загружаем эталонный эмбеддинг из {embedding_path}...")
                embedding = np.load(embedding_path)
            else:
                print(f"Создаем эталонный эмбеддинг из {ref_audio_path}...")
                if not ref_path.exists():
                    raise FileNotFoundError(f"Эталонный аудиофайл для '{speaker_name}' не найден: {ref_audio_path}")
                
                wav = preprocess_wav(ref_path)
                embedding = self.encoder.embed_utterance(wav)
                np.save(embedding_path, embedding)
                print(f"Эмбеддинг сохранен в {embedding_path}")
            
            self.reference_embeddings[speaker_name] = embedding

    def get_similarity_scores(self, audio_chunk: np.ndarray, sample_rate: int = 16000) -> Dict[str, float]:
        """
        Вычисляет схожесть с каждым спикером и возвращает словарь со всеми результатами.

        :param audio_chunk: Аудиофрагмент в виде NumPy массива.
        :param sample_rate: Частота дискретизации аудио.
        :return: Словарь вида {"имя_спикера": схожесть}.
        """
        if audio_chunk.size == 0 or not self.reference_embeddings:
            return {}
            
        # Предобработка аудио из массива NumPy
        wav = preprocess_wav(audio_chunk, source_sr=sample_rate)
        
        # Создаем эмбеддинг для нового чанка
        chunk_embed = self.encoder.embed_utterance(wav)
        
        scores: Dict[str, float] = {}

        # Вычисляем схожесть для каждого зарегистрированного спикера
        for speaker_name, ref_embed in self.reference_embeddings.items():
            similarity = np.dot(ref_embed, chunk_embed)
            scores[speaker_name] = similarity
        
        return scores