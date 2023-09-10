import os
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
import uuid
import cloudinary.uploader
import cloudinary.api
from .utils import (
    generate_ai_chatbot_response,
    generate_corrected_transcript_with_cloudinary_audio_file,
)

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)

ai_chatbot_bp = Blueprint("ai_chatbot", __name__)

@ai_chatbot_bp.route('/', methods=("GET", "POST"))
def index():
    return redirect(url_for("ai_chatbot.ai_chatbot"))

@ai_chatbot_bp.route('/ai-chatbot', methods=("GET", "POST"))
def ai_chatbot():
    messages = (
        request.args.get("messages")
        if request.args.get("messages")
        else [{"role": "system", "content": "What can I help you today?"}]
    )
    if request.method == "POST":
        prompt = request.form["input"]
        messages.append({"role": "user", "content": prompt})
        status, messages = generate_ai_chatbot_response(messages)
        return jsonify({"status": status, "messages": messages}), 200
    return render_template("index.html", messages=messages)


@ai_chatbot_bp.route('/speech-to-text', methods=("GET", "POST"))
def speech_to_text():
    if request.method == "POST":
        if "audio" in request.files:
            audio_file = request.files["audio"]
            if audio_file:
                # Generate a unique filename for the audio file
                folder = "open-ai-audio"
                filename = f"{str(uuid.uuid4())}.wav"
                # Save the audio file to the "open-ai-audio" folder in Cloudinary
                result = cloudinary.uploader.upload(
                    audio_file,
                    folder=folder,
                    resource_type="raw",
                    public_id=filename,
                    overwrite=True,
                )
                # Get the public URL of the uploaded audio file
                audio_url = result["secure_url"]
                (
                    status,
                    result,
                ) = generate_corrected_transcript_with_cloudinary_audio_file(audio_url)
                # Delete the file
                public_id = f"{folder}/{filename}"
                cloudinary.uploader.destroy(public_id, resource_type="raw")
                return jsonify({"status": status, "result": result}), 200
        return jsonify({"status": "error", "message": "No audio file received."})
    return redirect(url_for("ai_chatbot.ai_chatbot"))
