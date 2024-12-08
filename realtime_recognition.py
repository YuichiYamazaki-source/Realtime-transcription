'''録画はできるけど文字お越しができない状態'''

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
from datetime import datetime

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

FORMAT = pa.paInt16
SAMPLE_RATE = 44100    # サンプリングレート
CHANNELS = 1    # モノラル
INPUT_DEVICE_INDEX = 1    # マイクのチャンネル
CALL_BACK_FREQUENCY = 10     # コールバック呼び出しの周期[sec]
CHUNK = 1024    # 分割の間隔

audio_interface = pa.PyAudio()
sprec = sr.Recognizer()
finished_sign = False
audio_buffer = []

def callback(in_data, frame_count, time_info, status):
    """ 
    callback function are needed for realtime-texisting-audio if you use pyaudio
    """
    global sprec
    global audio_buffer

    # 音声データをバッファに蓄積
    audio_buffer.append(in_data)
    
    # バッファのデータを一定時間ごとにWAVファイルに保存(文字お越しと実際の音声の比較のため)
    if len(audio_buffer) >= int(SAMPLE_RATE * CALL_BACK_FREQUENCY):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"callback_audio_{timestamp}.wav"
        with wave.open(filename, "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio_interface.get_sample_size(FORMAT))
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(b''.join(audio_buffer))
        audio_buffer = []  # バッファをクリア

        # 音声データを認識
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

@eel.expose
def start_recognition():
    global finished_sign
    global thread
    finished_sign = False
    thread = threading.Thread(target=realtime_texting)
    logging.info("Info: Let's begin a Real-time texting!!")
    thread.start()

@eel.expose
def stop_recognition():
    global finished_sign
    finished_sign = True
    logging.info("Notice!: Stop the Realtime texting")

def realtime_texting():
    global finished_sign
    global audio_interface

    stream = audio_interface.open(format=FORMAT,
                                  channels=CHANNELS,
                                  rate=SAMPLE_RATE,
                                  input=True,
                                  frames_per_buffer=SAMPLE_RATE * CALL_BACK_FREQUENCY,
                                  stream_callback=callback)
    try:
        stream.start_stream()
        logging.info("Start Audio Streaming")
        
        while not finished_sign:
            time.sleep(0.1)  # CPU使用率を下げるために少し待機
        
        stream.stop_stream()
        stream.close()
        audio_interface.terminate()
        logging.info("Audio Streaming is finished")
        
    except sr.UnknownValueError:
        logging.error("Error!!:Audio Streaming is failed.")
    except sr.RequestError:
        logging.error("Error!!:Audio Streaming is failed in PyAudio")        
    except Exception as e:
        logging.error("Something wrong at streaming!!")

current_dir = os.path.dirname(os.path.abspath(__file__))
html_file = current_dir + "\web\index.html"

#eelアプリの開始
eel.init('web')
eel.start(html_file, mode='chrome-app', size=(700, 500), block=True)
logging.info("Makeing the web page...")