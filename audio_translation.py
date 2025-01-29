
import torch
import numpy as np
import sounddevice as sd
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor, MarianMTModel, MarianTokenizer

# Ensure this script runs only when called directly
if __name__ == "__main__":
    # Define the speech-to-text model and processor
    stt_model_name = "facebook/wav2vec2-large-960h"
    processor = Wav2Vec2Processor.from_pretrained(stt_model_name)
    stt_model = Wav2Vec2ForCTC.from_pretrained(stt_model_name)

    # Define the translation model and tokenizer
    translation_model_name = "Helsinki-NLP/opus-mt-en-fr"
    translator_tokenizer = MarianTokenizer.from_pretrained(translation_model_name)
    translator_model = MarianMTModel.from_pretrained(translation_model_name)

    def record_audio(duration=5, samplerate=16000):
        """
        Record audio for a specified duration and samplerate.
        """
        print("Recording... Press Ctrl+C to stop.")
        try:
            audio_data = sd.rec(
                int(duration * samplerate), samplerate=samplerate, channels=1, dtype="float32"
            )
            sd.wait()  # Wait until the recording is finished
            print("Recording finished.")
            return audio_data.flatten()
        except Exception as e:
            print(f"Error during recording: {e}")
            return None

    def transcribe_audio(audio_input, samplerate=16000):
        """
        Transcribe the recorded audio using the Wav2Vec2 model.
        """
        try:
            # Rescale audio to match the input range expected by Wav2Vec2
            audio_input = np.asarray(audio_input, dtype=np.float32)
            input_values = processor(
                audio_input, sampling_rate=samplerate, return_tensors="pt", padding=True
            ).input_values

            # Perform inference
            logits = stt_model(input_values).logits
            predicted_ids = torch.argmax(logits, dim=-1)

            # Decode transcription
            transcription = processor.decode(predicted_ids[0])
            return transcription
        except Exception as e:
            print(f"Error during transcription: {e}")
            return None

    def translate_text_to_french(text):
        """
        Translate English text into French using MarianMT.
        """
        try:
            inputs = translator_tokenizer(text, return_tensors="pt", padding=True, truncation=True)
            translated = translator_model.generate(**inputs)
            translation = translator_tokenizer.decode(translated[0], skip_special_tokens=True)
            return translation
        except Exception as e:
            print(f"Error during translation: {e}")
            return None

    def stream_audio():
        """
        Main function to stream audio, transcribe it, and translate it.
        """
        samplerate = 16000  # Sample rate for the Wav2Vec2 model
        duration = 5  # Duration of audio recording in seconds

        while True:
            try:
                audio_input = record_audio(duration, samplerate)
                if audio_input is not None:
                    transcription = transcribe_audio(audio_input, samplerate)
                    if transcription:
                        print(f"Transcription: {transcription}")
                        translation = translate_text_to_french(transcription)
                        if translation:
                            print(f"Translation (French): {translation}")
                else:
                    print("No audio input recorded.")
            except KeyboardInterrupt:
                print("\nStopped recording.")
                break

    # Run the audio streaming process
    stream_audio()
