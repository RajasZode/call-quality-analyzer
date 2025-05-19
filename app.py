# app.py
from flask import Flask, render_template, request
import os
import whisper
import time
from score_transcript import score_transcript, scoring_criteria
from dotenv import load_dotenv
import subprocess
from pyannote.audio import Pipeline

UPLOAD_FOLDER = "static/uploads"

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load Whisper model
whisper_model = whisper.load_model("small")
load_dotenv()

# Assign speaker tags more accurately based on midpoint overlap
def assign_tagged_transcript(whisper_segments, diarization):
    results = []
    for segment in whisper_segments:
        start, end, text = segment["start"], segment["end"], segment["text"]
        midpoint = (start + end) / 2
        speaker = "Unknown"
        for turn, _, label in diarization.itertracks(yield_label=True):
            if turn.start <= midpoint <= turn.end:
                speaker = label
                break
        results.append({
            "speaker": speaker,
            "start": round(start),
            "text": text.strip(),
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

            # Diarization
            pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=os.getenv("HUGGINGFACE_TOKEN"))
            diarization = pipeline(converted_path)

            # Transcription
            whisper_result = whisper_model.transcribe(converted_path, language="en", fp16=False)
            whisper_segments = whisper_result.get("segments", [])

            # Tag speakers
            transcript_blocks = assign_tagged_transcript(whisper_segments, diarization)

            # Combine all transcript text
            full_transcript = " ".join([block["text"] for block in transcript_blocks])

            # Score
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
    app.run(debug=True)
