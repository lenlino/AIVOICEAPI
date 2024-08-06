import asyncio
import os
import wave

import aiofiles
import clr
import time

from fastapi import Body, FastAPI, HTTPException
from fastapi.responses import FileResponse, Response
from starlette.responses import JSONResponse

VOICE_DICT = [
  {
    "name": "琴葉 茜",
    "styles": [
      {
        "name": "ノーマル",
        "id": 0,
        "raw_name": "琴葉 茜"
      },
      {
        "name": "蕾",
        "id": 1,
        "raw_name": "琴葉 茜（蕾）"
      }
    ],
  },
  {
    "name": "琴葉 葵",
    "styles": [
      {
        "name": "ノーマル",
        "id": 2,
        "raw_name": "琴葉 葵"
      },
      {
        "name": "蕾",
        "id": 3,
        "raw_name": "琴葉 葵（蕾）"
      }
    ],
  },
]
VOICE_DICT_FOR_GEN = {}
for voice in VOICE_DICT:
    for style in voice["styles"]:
        VOICE_DICT_FOR_GEN[id] = style["raw_name"]


COUNTER = 0

_editor_dir = os.environ['ProgramW6432'] + '\\AI\\AIVoice\\AIVoiceEditor\\'

app = FastAPI()

if not os.path.isfile(_editor_dir + 'AI.Talk.Editor.Api.dll'):
  print("A.I.VOICE Editor (v1.3.0以降) がインストールされていません。")
  exit()

# pythonnet DLLの読み込み
clr.AddReference(_editor_dir + "AI.Talk.Editor.Api")
from AI.Talk.Editor.Api import TtsControl, HostStatus

tts_control = TtsControl()

# A.I.VOICE Editor APIの初期化
host_name = tts_control.GetAvailableHostNames()[0]
tts_control.Initialize(host_name)

# A.I.VOICE Editorの起動
if tts_control.Status == HostStatus.NotRunning:
  tts_control.StartHost()

# A.I.VOICE Editorへ接続
tts_control.Connect()
host_version = tts_control.Version
print(f"{host_name} (v{host_version}) へ接続しました。")


# テキストを設定


# 再生

# A.I.VOICE Editorとの接続を終了する
#tts_control.Disconnect()
#print(f"{host_name} (v{host_version}) との接続を終了しました。")

@app.get("/speakers")
async def get_speakers():
    return JSONResponse(content=VOICE_DICT)

@app.post("/synthesis")
async def synthesis(text: str, speaker: int):
    print(tts_control.Status)
    while tts_control.Status != HostStatus.Idle:
        await asyncio.sleep(0.1)
    tts_control.Text = text
    tts_control.CurrentVoicePresetName = VOICE_DICT[speaker]
    #play_time = tts_control.GetPlayTime()
    #tts_control.Play()
    global COUNTER
    COUNTER += 1
    if COUNTER > 100:
        COUNTER = 0
    file_path = os.path.dirname(os.path.abspath(__file__)) + f"/audio/text{COUNTER}.wav"
    tts_control.SaveAudioToFile(file_path)
    async with aiofiles.open(file_path, mode='rb') as f:
        data: bytes = await f.read()
        return Response(data, media_type="audio/wav")

