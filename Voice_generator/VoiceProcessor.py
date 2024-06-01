import os
import threading
import time
from typing import Union

import pyaudio
import httpx
import logging
from queue import Queue, Empty

# Setup logging
#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class VoiceProcessor:
    """
    A class to process and generate audio from text using the OpenAI API.

    Attributes:
        api_key (str): The API key for accessing the OpenAI API.
        voice (str): The voice to use for text-to-speech. Can be specified by name or index.
        format (int): The format of the audio.
        channels (int): The number of audio channels.
        rate (int): The sample rate of the audio.
        chunk_size (int): The chunk size for streaming audio.
        sentence_queue (Queue): Queue to hold sentences to be processed.
        token_buffer (str): Buffer to hold tokens before they are processed into sentences.
        is_processing (threading.Event): Event to signal if processing is ongoing.
        stop_event (threading.Event): Event to signal if processing should stop.
        audio_thread (threading.Thread): Thread for processing audio.
        processing_lock (threading.Lock): Lock to ensure thread-safe operations.
    """
    ALLOWED_VOICES = {
        1: "alloy",
        2: "echo",
        3: "fable",
        4: "onyx",
        5: "nova",
        6: "shimmer"
    }

    def __init__(self, api_key, voice: Union[str, int] = "alloy"):
        """
        Initialize the VoiceProcessor with the provided API key and voice.

        Args:
            api_key (str): The API key for accessing the OpenAI API.
            voice (Union[str, int]): The voice to use for text-to-speech. Can be specified by name or index.
        """
        self.api_key = api_key
        self.voice = self.validate_voice(voice)
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 24000
        self.chunk_size = 1024
        self.sentence_queue = Queue()
        self.token_buffer = ""
        self.is_processing = threading.Event()
        self.stop_event = threading.Event()
        self.audio_thread = None
        self.processing_lock = threading.Lock()

    def validate_voice(self, voice: Union[str, int]) -> str:
        """
        Validate the provided voice and return the appropriate voice string.

        Args:
            voice (Union[str, int]): The voice to validate.

        Returns:
            str: The validated voice string.
        """
        if isinstance(voice, int):
            return self.ALLOWED_VOICES.get(voice, "alloy")
        elif isinstance(voice, str) and voice.lower() in self.ALLOWED_VOICES.values():
            return voice.lower()
        else:
            logging.warning(f"Invalid voice '{voice}' provided. Defaulting to 'alloy'.")
            return "alloy"

    def process_audio(self):
        """
        Process audio from the sentences in the queue and play it using PyAudio.
        """
        logging.debug("Initializing PyAudio")
        p = pyaudio.PyAudio()
        stream = p.open(format=self.format, channels=self.channels, rate=self.rate, output=True)
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        with httpx.Client() as client:
            while not self.stop_event.is_set() or not self.sentence_queue.empty():
                try:
                    sentence = self.sentence_queue.get(timeout=1)
                    logging.debug(f"Now generating audio for: {sentence}")
                except Empty:
                    continue

                if sentence is None:
                    break

                data = {
                    "model": "tts-1",
                    "voice": self.voice,
                    "input": str(sentence),
                    "response_format": "pcm"
                }

                try:
                    self.is_processing.set()
                    logging.debug("Sending request to OpenAI API")
                    response = client.post("https://api.openai.com/v1/audio/speech", headers=headers, json=data,
                                           timeout=60)
                    logging.debug("Request sent to OpenAI API")
                    response.raise_for_status()
                    logging.debug("Received response from OpenAI API")

                    for chunk in response.iter_bytes(self.chunk_size):
                        if chunk:
                            stream.write(chunk)
                    if self.stop_event.is_set() and self.sentence_queue.empty():
                        break

                except Exception as e:
                    logging.error(f"Error processing sentence '{sentence}': {e}")
                finally:
                    self.is_processing.clear()
                    self.sentence_queue.task_done()

        self.fade_out_audio(stream)
        stream.stop_stream()
        stream.close()
        p.terminate()

    def fade_out_audio(self, stream, duration=0.5):
        """
        Fade out the audio before stopping.

        Args:
            stream (pyaudio.Stream): The audio stream to fade out.
            duration (float): The duration of the fade out in seconds.
        """
        volume = 1.0
        fade_steps = int(self.rate / self.chunk_size * duration)
        for _ in range(fade_steps):
            volume *= 0.9
            silence = (b'\x00' * self.chunk_size) * int(1 - volume)
            stream.write(silence)
            time.sleep(duration / fade_steps)

    def add_text_to_queue(self, text):
        """
        Add text to the processing queue.

        Args:
            text (str): The text to add to the queue.
        """
        with self.processing_lock:
            paragraphs = text.split('\n\n')
            for paragraph in paragraphs:
                self.sentence_queue.put(paragraph.strip())
            logging.debug(f"Added text to queue: {paragraphs}")
            self._ensure_audio_processing_started()

    def add_token(self, token):
        """
        Add a token to the buffer and process if needed.

        Args:
            token (str): The token to add to the buffer.
        """
        with self.processing_lock:
            self.token_buffer += token
            self.check_and_process_tokens()
            self._ensure_audio_processing_started()

    def check_and_process_tokens(self):
        """
        Check the buffer and add complete sentences to the queue.
        """
        while "\n\n" in self.token_buffer:
            parts = self.token_buffer.split("\n\n", 1)
            self.sentence_queue.put(parts[0].strip())
            logging.debug(f"Added to queue from token buffer: {parts[0].strip()}")
            self.token_buffer = parts[1].strip()
        if not self.stop_event.is_set() and self.token_buffer:
            logging.debug(f"Remaining in token buffer: {self.token_buffer}")

    def finalize_tokens(self):
        """
        Finalize any remaining tokens in the buffer.
        """
        with self.processing_lock:
            if self.token_buffer:
                self.sentence_queue.put(self.token_buffer.strip())
                logging.debug(f"Final added to queue from token buffer: {self.token_buffer.strip()}")
                self.token_buffer = ""

    def _ensure_audio_processing_started(self):
        """
        Ensure the audio processing thread is started.
        """
        if self.audio_thread is None or not self.audio_thread.is_alive():
            self.start_audio_processing()

    def start_audio_processing(self):
        """
        Start the audio processing thread.
        """
        self.stop_event.clear()
        self.audio_thread = threading.Thread(target=self.process_audio, daemon=True)
        self.audio_thread.start()

    def stop_audio_processing(self):
        """
        Stop the audio processing thread.
        """
        self.stop_event.set()
        if self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join()
        self.clear_queues()

    def clear_queues(self):
        """
        Clear all queues.
        """
        with self.sentence_queue.mutex:
            self.sentence_queue.queue.clear()
        self.token_buffer = ""
        self.is_processing.clear()

    def reset_audio_playback(self):
        """
        Reset the audio playback.
        """
        self.stop_audio_processing()
        self.start_audio_processing()

    def wait_for_completion(self):
        """
        Wait for all sentences to be processed.
        """
        self.sentence_queue.join()
        self.stop_audio_processing()


# Example usage
if __name__ == "__main__":
    # Retrieve your OpenAI API key from environment variables
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Please set the OPENAI_API_KEY environment variable.")

    # Initialize the VoiceProcessor with the API key and desired voice
    processor = VoiceProcessor(api_key, voice=3)  # You can change the voice here

    # Example text with paragraphs to be processed
    text = """This is the first paragraph.

This is the second paragraph, which is a bit longer and might need more processing time.

Here is the third paragraph."""

    # Add the text to the processing queue
    processor.add_text_to_queue(text)

    # Example tokens being added to the processing queue
    tokens = ["Token 1, ", "token 2,", "Token 3 are processed as one sentence\n\n", "Token 4, ", "token 5."]
    for token in tokens:
        processor.add_token(token)
        time.sleep(0.5)  # Simulate a delay between receiving tokens

    # Finalize any remaining tokens in the buffer
    processor.finalize_tokens()

    # Wait for all processing to complete before exiting
    processor.wait_for_completion()
