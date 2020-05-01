# -*- coding: utf-8 -*-

from huaweicloud_sis.client.tts_client import TtsClient
from huaweicloud_sis.bean.tts_request import TtsRequest
from huaweicloud_sis.bean.sis_config import SisConfig
from huaweicloud_sis.exception.exceptions import ClientException
from huaweicloud_sis.exception.exceptions import ServerException
from urllib.request import urlopen
from urllib.request import Request
from urllib.error import URLError
from urllib.parse import urlencode
from playsound import playsound
import json
import pyaudio
import wave
import sys
import base64
import time
import urllib


def audio_record(out_file, rec_time):
    '''
    用Pyaudio库录制音频
    out_file:输出音频文件名
    rec_time:音频录制时间(秒)
    '''
    CHUNK = 1024
    FORMAT = pyaudio.paInt16  # 16bit编码格式
    CHANNELS = 1  # 单声道
    RATE = 16000  # 16000采样频率

    p = pyaudio.PyAudio()
    # 创建音频流
    stream = p.open(format=FORMAT,  # 音频流wav格式
                    channels=CHANNELS,
                    rate=RATE,  # 采样率16000
                    input=True,
                    frames_per_buffer=CHUNK)

    print("Start Recording...")

    frames = []  # 录制的音频流
    # 录制音频数据
    for i in range(0, int(RATE / CHUNK * rec_time)):
        data = stream.read(CHUNK)
        frames.append(data)

    # 录制完成
    stream.stop_stream()
    stream.close()
    p.terminate()

    print("Recording Done...")

    # 保存音频文件
    wf = wave.open(out_file, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()


class DemoError(Exception):
    pass


def fetch_token():
    """  TOKEN start """
    TOKEN_URL = 'http://openapi.baidu.com/oauth/2.0/token'
    # API_KEY = 'oxWbu1xSZzt7sSmoMhOPRdQP'
    # SECRET_KEY = 'HAnet39TiFXEQUgHfOhTV4ERiuwzwGko'
    SCOPE = 'audio_voice_assistant_get'  # 有此scope表示有asr能力，没有请在网页里勾选，非常旧的应用可能没有
    params = {'grant_type': 'client_credentials',
              'client_id': API_KEY,
              'client_secret': SECRET_KEY}
    post_data = urlencode(params)

    post_data = post_data.encode('utf-8')
    req = Request(TOKEN_URL, post_data)
    try:
        f = urlopen(req)
        result_str = f.read()
    except URLError as err:
        print('token http response http code : ' + str(err.code))
        result_str = err.read()
    result_str = result_str.decode()
    # print(result_str)
    result = json.loads(result_str)
    # print(result)
    if ('access_token' in result.keys() and 'scope' in result.keys()):
        # print(SCOPE)
        # SCOPE = False 忽略检查
        if SCOPE and (not SCOPE in result['scope'].split(' ')):
            raise DemoError('scope is not correct')
        # print('SUCCESS WITH TOKEN: %s  EXPIRES IN SECONDS: %s' %
            #   (result['access_token'], result['expires_in']))
        return result['access_token']
    else:
        raise DemoError(
            'MAYBE API_KEY or SECRET_KEY not correct: access_token or scope not found in token response')


def wav_to_text(AUDIO_FILE):
    '''百度语音转文本api'''
    # 需要识别的文件  # 只支持 pcm/wav/amr 格式，极速版额外支持m4a 格式
    # 文件格式
    FORMAT = AUDIO_FILE[-3:]  # 文件后缀只支持 pcm/wav/amr 格式，极速版额外支持m4a 格式

    CUID = '123456PYTHON'
    # 采样率
    RATE = 16000  # 固定值

    # 普通版

    DEV_PID = 1537  # 1537 表示识别普通话，使用输入法模型。根据文档填写PID，选择语言及识别模型
    ASR_URL = 'http://vop.baidu.com/server_api'

    token = fetch_token()

    speech_data = []
    with open(AUDIO_FILE, 'rb') as speech_file:
        speech_data = speech_file.read()

    length = len(speech_data)
    if length == 0:
        raise DemoError('file %s length read 0 bytes' % AUDIO_FILE)
    speech = base64.b64encode(speech_data)

    speech = str(speech, 'utf-8')
    params = {'dev_pid': DEV_PID,
              # "lm_id" : LM_ID,    #测试自训练平台开启此项
              'format': FORMAT,
              'rate': RATE,
              'token': token,
              'cuid': CUID,
              'channel': 1,
              'speech': speech,
              'len': length
              }
    post_data = json.dumps(params, sort_keys=False)
    # print post_data
    req = Request(ASR_URL, post_data.encode('utf-8'))
    req.add_header('Content-Type', 'application/json')
    try:
        begin = time.perf_counter()
        f = urlopen(req)
        result_str = f.read()
        # print("Request time cost %f" % (time.perf_counter() - begin))
    except URLError as err:
        # print('asr http response http code : ' + str(err.code))
        result_str = err.read()

    result_str = str(result_str, 'utf-8')
    # print(result_str)

    result = json.loads(result_str)["result"][0]
    # print(result)
    # with open("result.txt", "w") as of:
    #     of.write(result_str)
    return result


def tts_example(text):
    """ 华为云sis语音合成 """
    # ak = 'GVOC7YSBOBAO3VZ38TPW'
    # sk = 'EpbGXUHTHoffHjj07W8UNWsGhxNEnEPESp7Gr6Qj'
    region = 'cn-north-1'
    path = RESULT_FILE

    # step1 初始化客户端
    config = SisConfig()
    config.set_connect_timeout(10)       # 设置连接超时
    config.set_read_timeout(10)         # 设置读取超时
    # 设置代理，使用代理前一定要确保代理可用。 代理格式可为[host, port] 或 [host, port, username, password]
    # config.set_proxy(proxy)
    tts_client = TtsClient(ak, sk, region, sis_config=config)

    # step2 构造请求
    tts_request = TtsRequest(text)
    # 设置请求，所有参数均可不设置，使用默认参数
    # 设置发声人，默认xiaoyan，xiaoqi 正式女生xiaoyu正式男生xiaoyan情感女生xiaowang童声
    tts_request.set_voice_name('xiaoyan')
    # 设置采样率，默认8k
    tts_request.set_sample_rate('8k')
    # 设置音量，[-20, 20]，默认0
    tts_request.set_volume(0)
    # 设置音高, [-500, 500], 默认0
    tts_request.set_pitch_rate(2)
    # 设置音速, [-500, 500], 默认0
    tts_request.set_speech_speed(-10)
    # 设置是否保存，默认False
    tts_request.set_saved(True)

    # 设置保存路径，只有设置保存，此参数才生效
    tts_request.set_saved_path(path)
    # print("已合成"+path)

    # # step3 发送请求，返回结果,格式为json. 如果设置保存，可在指定路径里查看保存的音频
    try:
        result = tts_client.get_tts_response(tts_request)
    except ClientException as e:
        print(e)
    except ServerException as e:
        print(e)
    # print(json.dumps(result, indent=2, ensure_ascii=False))


def tuling_response(text):
    api_url = "http://openapi.tuling123.com/openapi/api/v2"
    # text = '你好呀'

    req = {
        "perception":
        {
            "inputText":
            {
                "text": text
            },

            "selfInfo":
            {
                "location":
                {
                    "city": "广东",
                    "province": "深圳",
                }
            }
        },

        "userInfo":
        {
            "apiKey": apiKey,
            "userId": userId
        }
    }
    # print(req)
    # 将字典格式的req编码为utf8
    req = json.dumps(req).encode('utf8')
    # print(req)
    http_post = urllib.request.Request(api_url, data=req, headers={
                                       'content-type': 'application/json'})
    response = urllib.request.urlopen(http_post)
    response_str = response.read().decode('utf8')
    # print(response_str)
    response_dic = json.loads(response_str)
    print(response_dic)

    # intent_code = response_dic['intent']['code']
    results_text = response_dic['results'][0]['values']['text']
    print("我:"+text)
    print('AILIN：'+results_text)
    # print('code：' + str(intent_code))
    # print('text：' + results_text)
    return results_text


if __name__ == '__main__':
    # 语音文件
    AUDIO_FILE = './audio/temp.wav'
    RESULT_FILE = './audio/result.wav'
    # 百度api
    API_KEY = 'oxWbu1xSZzt7sSmoMhOPRdQP'
    SECRET_KEY = 'HAnet39TiFXEQUgHfOhTV4ERiuwzwGko'
    # 华为云api
    ak = 'GVOC7YSBOBAO3VZ38TPW'
    sk = 'EpbGXUHTHoffHjj07W8UNWsGhxNEnEPESp7Gr6Qj'
    # 图灵机器人
    apiKey = '7529129cf0d64810abcc8b8ff1841bd2'
    userId = '385537'
    while True:
        audio_record(AUDIO_FILE, 5)
        speechText = wav_to_text(AUDIO_FILE)
        if "退出" in speechText:
            tts_example('好吧再见')
            playsound(RESULT_FILE)
            break
        resultText = tuling_response(speechText)
        tts_example(resultText)
        playsound(RESULT_FILE)
