from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import tempfile
from pydub import AudioSegment
import io
import speech_recognition as sr
from googletrans import Translator

app = FastAPI()

recognizer = sr.Recognizer()
translator = Translator()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    audio_data = b""

    try:
        while True:
            # Receive audio chunks
            data = await websocket.receive_bytes()
            audio_data += data

            # Process audio when enough data is received
            if len(audio_data) > 32000:  # Buffer size for ~2 seconds of audio
                with tempfile.NamedTemporaryFile(delete=True, suffix=".wav") as temp_audio:
                    # Convert audio to WAV format for recognition
                    audio_segment = AudioSegment.from_file(io.BytesIO(audio_data), format="webm")
                    audio_segment.export(temp_audio.name, format="wav")

                    with sr.AudioFile(temp_audio.name) as source:
                        audio = recognizer.record(source)
                        try:
                            transcription = recognizer.recognize_google(audio)
                            translation = translator.translate(transcription, src="en", dest="fr").text

                            # Send back the transcription and translation
                            await websocket.send_json({
                                "transcription": transcription,
                                "translation": translation
                            })
                        except Exception as e:
                            print(f"Error during recognition: {e}")

                # Clear the buffer
                audio_data = b""

    except Exception as e:
        print(f"WebSocket connection closed: {e}")
    finally:
        await websocket.close()
