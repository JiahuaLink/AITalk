# -*- coding: utf-8 -*-
import pyaudio
import wave
import numpy as np

def Monitor():
    CHUNK = 512
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 48000
    RECORD_SECONDS = 10
    WAVE_OUTPUT_FILENAME = "cache.wav"
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    print("开始缓存录音")
    frames = []
    recordTime = 0
    isRecord = False
    while (True):
        # print( 'begin ')
        for i in range(0, 100):
            data = stream.read(CHUNK)
            frames.append(data)
        audio_data = np.fromstring(data, dtype=np.short)
        large_sample_count = np.sum( audio_data > 100 )
        temp = np.max(audio_data)
        if large_sample_count >0:
            isRecord = True
        if isRecord and temp <100:
            recordTime +=1
            if recordTime == 3:
                break
        print( "检测到信号")
        print( '当前阈值：',temp )
        print( 'large_sample_count：',large_sample_count )
        # print( 'large_sample_count:',large_sample_count )
    stream.stop_stream()
    stream.close()
    p.terminate()
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

if __name__ == '__main__':
    Monitor()