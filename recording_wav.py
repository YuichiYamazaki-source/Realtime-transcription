import pyaudio
import wave

FORMAT = pyaudio.paInt16
SAMPLE_RATE = 44100
CHANNELS = 1
CHUNK = 1024
RECORD_SECONDS = 5
OUTPUT_FILENAME = "test_audio.wav"

audio_interface = pyaudio.PyAudio()

# 録音用のストリームを開く
stream = audio_interface.open(format=FORMAT,
                              channels=CHANNELS,
                              rate=SAMPLE_RATE,
                              input=True,
                              frames_per_buffer=CHUNK)

print("Recording...")

frames = []

# 指定された秒数だけ録音する
for i in range(0, int(SAMPLE_RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

print("Finished recording.")

# ストリームを停止し、閉じる
stream.stop_stream()
stream.close()
audio_interface.terminate()

# 録音したデータをWAVファイルに保存する
with wave.open(OUTPUT_FILENAME, 'wb') as wf:
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio_interface.get_sample_size(FORMAT))
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(b''.join(frames))

print(f"Saved recording to {OUTPUT_FILENAME}")