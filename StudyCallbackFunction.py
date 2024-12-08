import time
import datetime
import eel
import threading
import os
import pyaudio as pa
import wave
import numpy as np
import logging
import speech_recognition as sr

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

FORMAT = pa.paInt16
SAMPLE_RATE = 44100    # サンプリングレート
CHANNELS = 1    # モノラルかバイラルか
INPUT_DEVICE_INDEX = 1    # マイクのチャンネル
CALL_BACK_FREQUENCY = 3     # コールバック呼び出しの周期[sec]
CHUNK = 1024    # 分割の間隔
audio_buffer = []    # 音声データのバッファ
#PyAudioのインスタンス用
# speech_recognitionのインスタンス用

audio_interface = pa.PyAudio()
sprec = sr.Recognizer()

def look_for_audio_input():
    """
    explain  information of audio devices on PC
    """
    
    _pa = pa.PyAudio()
    
    for i in range(_pa.get_device_count()):
        print(_pa.get_device_info_by_index(i))
        print()
    
    _pa.terminate()

def callback(in_data, frame_count, time_info, status):
    """ 
    callback function are needed for realtime-texisting-audio if you use pyaudio
    """
    global sprec
    global audio_buffer

    # 音声データをバッファに蓄積
    audio_buffer.append(in_data)
    
    # バッファのデータを一定時間ごとにWAVファイルに保存
    if len(audio_buffer) >= int(SAMPLE_RATE / CHUNK * CALL_BACK_FREQUENCY):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"callback_audio_{timestamp}.wav"
        with wave.open(filename, "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio_interface.get_sample_size(FORMAT))
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(b''.join(audio_buffer))
        audio_buffer = []  # バッファをクリア

    audio_data = sr.AudioData(b''.join(audio_buffer), SAMPLE_RATE, 2)
    
    try:
        sprec_text = sprec.recognize_google(audio_data, language='ja-JP')
        logging.info(f"Recognized: {sprec_text}")
        eel.updateTranscript(sprec_text)
        logging.info("eel.updateTranscript called")
    except sr.UnknownValueError:
        logging.error("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        logging.error(f"Could not request results from Google Speech Recognition service; {e}")
    return (in_data, pa.paContinue)

def realtime_texting(FORMAT=FORMAT, RATE=SAMPLE_RATE, CHANNELS=CHANNELS, INPUT_DEVICE_INDEX=INPUT_DEVICE_INDEX, CHUNK=CHUNK):
    global audio_interface
    global finished_sign
    
    stream = audio_interface.open(
                        format             = FORMAT,
                        rate               = SAMPLE_RATE,
                        channels           = CHANNELS,
                        input_device_index = INPUT_DEVICE_INDEX,
                        input              = True, 
                        frames_per_buffer  = CHUNK,
                        stream_callback   = callback
                        )
    try:
        stream.start_stream()
        logging.info("Start Audio Streaming")
        
        while not finished_sign:
            time.sleepo(3)
        
        stream.stop_stream()
        stream.close()
        audio_interface.terminate()
        logging.info("Audio Streaming is finished")
        
    except sr.UnknownValueError:
        logging.error("Error!!:Audio Streaming is failed.")
        pass
    except sr.RequestError:
        logging.error("Error!!:Audio Streamig is failed in PyAudio")        
        pass
    except Exception as e:
        logging.error("Something wrong at streaming!!")

@eel.expose
def start_recognition():
    global finished_sign    # ボタン押したら終了のお知らせ
    global thread
    finished_sign = False
    thread = threading.Thread(target=realtime_texting)
    logging.info("Info:Let's beging a Real-time texting!!")
    thread.start()
    
@eel.expose
def stop_recognition():
    global finished_sign
    finished_sign = True
    logging.info("Notice!:Stop the Realtime texting")
    
current_dir = os.path.dirname(os.path.abspath(__file__))
html_file = current_dir + "\web\index.html"

look_for_audio_input()

#eelアプリの開始
eel.init('web')
eel.start(html_file, mode='chrome-app', size=(700, 500), block=True)
logging.info("Makeing the web page...")
