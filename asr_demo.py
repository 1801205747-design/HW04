import sys
import os
import wave
import json
import sounddevice as sd
import numpy as np
from vosk import Model, KaldiRecognizer

# 初始化Vosk模型
MODEL_PATH = "model"
if not os.path.exists(MODEL_PATH):
    print("请先下载Vosk中文模型并解压到model文件夹！")
    sys.exit(1)
model = Model(MODEL_PATH)

# 功能1：识别本地音频文件（支持wav格式，16kHz/单声道）
def recognize_audio_file(audio_path):
    if not os.path.exists(audio_path):
        print(f"音频文件{audio_path}不存在！")
        return
    wf = wave.open(audio_path, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        print("音频文件需为16kHz、单声道、16位深度的wav格式！")
        return
    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)
    print("开始识别音频文件...")
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            res = json.loads(rec.Result())
            if "text" in res:
                print(f"识别结果：{res['text']}")
    final_res = json.loads(rec.FinalResult())
    print(f"最终识别结果：{final_res['text']}")

# 功能2：麦克风实时识别
def recognize_microphone():
    samplerate = 16000
    rec = KaldiRecognizer(model, samplerate)
    rec.SetWords(True)
    print("开始麦克风实时识别（按Ctrl+C停止）...")
    try:
        with sd.InputStream(samplerate=samplerate, channels=1, dtype='int16', blocksize=8000, callback=lambda indata, frames, time, status: rec.AcceptWaveform(indata.tobytes())):
            while True:
                if rec.PartialResult():
                    part_res = json.loads(rec.PartialResult())
                    print(f"实时识别中：{part_res['partial']}", end='\r')
                if rec.AcceptWaveform(b""):
                    res = json.loads(rec.Result())
                    if "text" in res:
                        print(f"\n确认识别：{res['text']}")
    except KeyboardInterrupt:
        print("\n停止识别！")
        final_res = json.loads(rec.FinalResult())
        print(f"最终实时识别结果：{final_res['text']}")

if __name__ == "__main__":
    # 模式选择：1=音频文件识别，2=麦克风实时识别
    mode = input("请选择识别模式（1=音频文件，2=麦克风实时）：")
    if mode == "1":
        audio_path = input("请输入wav音频文件路径：")
        recognize_audio_file(audio_path)
    elif mode == "2":
        recognize_microphone()
    else:
        print("无效模式！")