import whisper

model = whisper.load_model("base")  # Or use "small" or "medium" later
result = model.transcribe("sample.mp3")  # Replace with your audio file name
print(result["text"])