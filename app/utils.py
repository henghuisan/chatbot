import os
import io
import requests
import openai
from openai.error import InvalidRequestError

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_ai_chatbot_response(messages):
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages
        )
        reply = completion.choices[0].message.content
        messages.append({"role": "system", "content": reply})
        return "success", messages
    except InvalidRequestError as e:
        return "fail", str(e)


def generate_corrected_transcript_with_cloudinary_audio_file(audio_url):
    try:
        # Fetch the audio file as bytes using requests
        response = requests.get(audio_url)
        audio_data = response.content
        # Create a io.BufferedReader object from the bytes data and set the name attribute
        audio_buffer = io.BytesIO(audio_data)
        audio_buffer.name = "user_voice_input.wav"  # Replace with the desired filename
        # Pass the temporary file to the translate method
        transcript = openai.Audio.translate("whisper-1", audio_buffer)
        result = transcript.text
        return "success", result
    except InvalidRequestError as e:
        return "fail", str(e)
