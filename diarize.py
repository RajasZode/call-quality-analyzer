from pyannote.audio import Pipeline
import os
from dotenv import load_dotenv

load_dotenv()

try:
# Use token from environment variable
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization@2023.07", use_auth_token=os.getenv("HUGGINGFACE_TOKEN"))
except Exception as e:
    import traceback
    traceback.print_exc()

# Path to your test audio file
AUDIO_FILE = "clean_call.wav"

# Apply diarization
diarization = pipeline(AUDIO_FILE)

# Print diarized output
for turn, _, speaker in diarization.itertracks(yield_label=True):
    print(f"{turn.start:.1f}s - {turn.end:.1f}s: {speaker}")