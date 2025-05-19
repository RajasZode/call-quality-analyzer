# app.py
from flask import Flask, render_template, request
import os
import whisper
import time
from score_transcript import score_transcript, scoring_criteria
from dotenv import load_dotenv
import subprocess

UPLOAD_FOLDER = "static/uploads"
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load Whisper model
whisper_model = whisper.load_model("tiny")
load_dotenv()

# Dummy speaker tagging (since diarization fails on Render Free)
def assign_tagged_transcript(segments):
    results = []
    for idx, segment in enumerate(segments):
        speaker = "Speaker_01" if idx % 2 == 0 else "Speaker_02"
        results.append({
            "speaker": speaker,
            "start": round(segment["start"]),
            "text": segment["text"].strip(),
            "side": "left"
        })
    return results

# Score summary sentence
def generate_summary(scores):
    summary_lines = []
    for category, (score, total) in scores.items():
        percent = (score / total) * 100 if total > 0 else 0
        if percent >= 80:
            summary_lines.append(f"{category} was handled very well.")
        elif percent >= 40:
            summary_lines.append(f"{category} was average and can be improved.")
        else:
            summary_lines.append(f"{category} was poorly handled and needs attention.")
    return " ".join(summary_lines)

@app.route('/', methods=['GET', 'POST'])
def index():
    transcript_blocks = []
    scores = {}
    overall_score = (0, 0)
    audio_preview_path = None
    summary_text = ""
    missed_checkpoints = {}

    if request.method == 'POST':
        audio_file = request.files['audio']
        if audio_file:
            filename = audio_file.filename
            original_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            audio_file.save(original_path)

            # Convert to 16kHz mono WAV
            converted_filename = "clean_test.wav"
            converted_path = os.path.join(app.config['UPLOAD_FOLDER'], converted_filename)
            subprocess.run(["ffmpeg", "-y", "-i", original_path, "-ac", "1", "-ar", "16000", converted_path])

            # Transcription (no diarization)
            whisper_result = whisper_model.transcribe(converted_path, language="en", fp16=False)
            segments = whisper_result.get("segments", [])

            # Assign dummy speakers
            transcript_blocks = assign_tagged_transcript(segments)

            # Combine transcript text
            full_transcript = " ".join([b["text"] for b in transcript_blocks])

            # Scoring
            scored_output = score_transcript(full_transcript, scoring_criteria)
            scores = {k: (v["score"], v["max_score"]) for k, v in scored_output.items()}
            missed_checkpoints = {k: v["missed"] for k, v in scored_output.items()}
            total = sum(v["score"] for v in scored_output.values())
            max_total = sum(v["max_score"] for v in scored_output.values())
            overall_score = (total, max_total)
            summary_text = generate_summary(scores)
            audio_preview_path = f'uploads/{converted_filename}'

    return render_template(
        'index.html',
        transcript_blocks=transcript_blocks,
        scores=scores,
        overall=overall_score,
        audio_path=audio_preview_path,
        summary_text=summary_text,
        missed_checkpoints=missed_checkpoints
    )

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)