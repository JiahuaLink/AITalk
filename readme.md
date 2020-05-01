# python人工智能语音聊天服务
## 一、实现思路
### 1、录制音频使用python audio模块
使用PyAudio录音并保存音频文件在本地

### 2、语音文件转文本
 将缓存音频的文件百度语音识别api转为文本  
 https://ai.baidu.com/ai-doc/SPEECH/Ek39uxgre
### 3、使用文本与机器人交互
 利用图灵api获取机器人回答text  
 http://www.turingapi.com/
 
### 4、交互结果文本转语音
采用华为云语音交互服务api将文本转语音，最后播放
https://support.huaweicloud.com/sis/index.html
