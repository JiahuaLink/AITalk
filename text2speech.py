# -*- coding: utf-8 -*-

from huaweicloud_sis.client.tts_client import TtsClient
from huaweicloud_sis.bean.tts_request import TtsRequest
from huaweicloud_sis.bean.sis_config import SisConfig
from huaweicloud_sis.exception.exceptions import ClientException
from huaweicloud_sis.exception.exceptions import ServerException
import json

def tts_example(text):
    """ 语音合成demo """
    ak = 'GVOC7YSBOBAO3VZ38TPW'
    sk = 'EpbGXUHTHoffHjj07W8UNWsGhxNEnEPESp7Gr6Qj'
    region = 'cn-north-1'     # region，如cn-north-1
    # text = '欢迎在win10系统中，默认使用的是微软输入法。最近有用户反应称使用微软输入法打出来的字都是繁体的，该怎么办？出现这样的情况是因为微软输入法本身支持简体和繁体输入，并且可以通过快捷键切换，我们只需按下面步骤进行设置即可还原成简单！'
    path = 'huawei.wav'       # 保存路径，需要具体到音频文件，如D:/test.wav，可在设置中选择不保存本地

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

    # # step3 发送请求，返回结果,格式为json. 如果设置保存，可在指定路径里查看保存的音频
    try:
        result = tts_client.get_tts_response(tts_request)
    except ClientException as e:
        print(e)
    except ServerException as e:
        print(e)
    # print(json.dumps(result, indent=2, ensure_ascii=False))
    print("已合成"+path)


if __name__ == '__main__':
    text = '定制语音合成，是一种将文本转换成逼真语音的服务。用户通过实时访问和调用API获取语音合成结果，将用户输入的文字合成为音频。通过音色选择、自定义音量、语速，为企业和个人提供个性化的发音服务。'

    tts_example(text)

