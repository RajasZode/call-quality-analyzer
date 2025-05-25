from flask import Flask, render_template, request
import os
import whisper
import subprocess
from score_transcript import score_transcript, scoring_criteria
from dotenv import load_dotenv
from pyannote.audio import Pipeline

UPLOAD_FOLDER = "static/uploads"
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load Whisper model
whisper_model = whisper.load_model("tiny")
load_dotenv()

try:
    # Real speaker tagging using pyannote
    token = os.getenv("HUGGINGFACE_TOKEN")
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=token)
    if pipeline is None:
        raise ValueError(f"Pipeline is Returning None {pipeline}")
except Exception as e:
    import traceback
    traceback.print_exc()


def assign_tagged_transcript(segments, diarization):
    results = []
    for segment in segments:
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

# Generate summary text and call_summary dictionary
def generate_summary_and_call_summary(scores):
    summary_lines = []
    call_summary = {}
    for category, (score, total) in scores.items():
        percent = (score / total) * 100 if total > 0 else 0
        if percent >= 80:
            text = f"{category} was handled very well."
        elif percent >= 40:
            text = f"{category} was average and can be improved."
        else:
            text = f"{category} was poorly handled and needs attention."
        summary_lines.append(text)
        call_summary[category] = text
    return " ".join(summary_lines), call_summary

# Landing page
@app.route('/')
def landing():
    return render_template('landing.html')

# Upload and analyze route
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    transcript_blocks = []
    scores = {}
    overall_score = (0, 0)
    audio_preview_path = None
    summary_text = ""
    call_summary = {}
    missed_checkpoints = {}
    achieved_checkpoints = {}

    if request.method == 'POST':
        audio_file = request.files['audio']
        if audio_file:
            filename = audio_file.filename
            original_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            audio_file.save(original_path)

            # Convert to 16kHz mono WAV
            converted_filename = "clean_test.wav"
            converted_path = os.path.join(app.config['UPLOAD_FOLDER'], converted_filename)
            subprocess.run([
                "ffmpeg", "-y", "-i", original_path,
                "-ac", "1", "-ar", "16000", converted_path
            ])

            # Diarization
            diarization = pipeline(converted_path)

            # Transcribe
            whisper_result = whisper_model.transcribe(converted_path, language="en", fp16=False)
            segments = whisper_result.get("segments", [])

            transcript_blocks = assign_tagged_transcript(segments, diarization)
            full_transcript = " ".join([b["text"] for b in transcript_blocks])

            # Scoring
            scored_output = score_transcript(transcript_blocks, scoring_criteria)
            scores = {k: (v["score"], v["total"]) for k, v in scored_output.items()}
            missed_checkpoints = {k: v["missed"] for k, v in scored_output.items()}
            achieved_checkpoints = {k: v["achieved"] for k, v in scored_output.items()}
            total = sum(v["score"] for v in scored_output.values())
            max_total = sum(v["total"] for v in scored_output.values())
            overall_score = (total, max_total)
            summary_text, call_summary = generate_summary_and_call_summary(scores)
            audio_preview_path = f'uploads/{converted_filename}'

    return render_template(
        'index.html',
        transcript_blocks=transcript_blocks,
        scores=scores,
        overall=overall_score,
        audio_path=audio_preview_path,
        summary_text=summary_text,
        call_summary=call_summary,
        missed_checkpoints=missed_checkpoints,
        achieved_checkpoints=achieved_checkpoints
    )

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=False,host="0.0.0.0",  port=5050)
