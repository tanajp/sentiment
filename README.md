# トピック推定&ネガポジ判定LineBot

## 概要
ニュース記事のタイトルなどを入力すると、その記事のトピックを推定し、タイトルから記事の内容が   
ネガティブなのか、ポジティブなのかを推測してくれる。

<br>

## 開発環境
Python 3.7.4  

<br>

## 使用サービス
[LINE Messaging API](https://developers.line.biz/ja/services/messaging-api/)  
[Text Classification API](https://a3rt.recruit-tech.co.jp/product/textClassification/)   
[HEROKU](https://jp.heroku.com/)    
[単語感情極性対応表](http://www.lr.pi.titech.ac.jp/~takamura/pubs/pn_ja.dic)  

<br>

## 必要なファイル
| ファイル名 | 役割 |
----|---- 
| Procfile | Flask + gunicorn プログラム実行方法 |
| runtime.txt | 自身のPythonのバージョンを記述 |
| requirements.txt | 必要なライブラリを記述 |
| app.py | ソースコード |
| polarity.txt | 単語感情極性対応表 |

<br>

## ソースコード
```python
import os
import pya3rt
from janome.tokenizer import Tokenizer
import requests

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)

line_channel_secret = "************************"  #自身のチャネルシークレット
line_channel_access_token = "******************************"  #自身のチャネルアクセストークン

line_bot_api = LineBotApi(line_channel_access_token)
handler = WebhookHandler(line_channel_secret)


@app.route("/callback", methods=['POST'])
def callback():

    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
    push_text = event.message.text
    reply_text1 = textapi_response(push_text)
    reply_text2 = judge_polarity(push_text)
    messages = [
        TextSendMessage(text=reply_text1),
        TextSendMessage(text=reply_text2),
    ]

    line_bot_api.reply_message(event.reply_token, messages)

dict_polarity = {}
with open('./polarity.txt', 'r') as f:
    line = f.read()
    lines = line.split('\n')
    for i in range(len(lines)):
        linecomponents = lines[i].split(':')
        dict_polarity[linecomponents[0]] = linecomponents[3]

def judge_polarity(text):
    t = Tokenizer()
    tokens = t.tokenize(text)
    pol_val = 0
    for token in tokens:
        word = token.surface
        pos = token.part_of_speech.split(',')[0]
        if word in dict_polarity:
            pol_val += float(dict_polarity[word])
            pol_val = round(pol_val, 5)

    if pol_val > 0.3:
        return "ポジティブです。\nScore: " + str(pol_val)
    elif pol_val < -0.3:
        return "ネガティブです。\nScore: " + str(pol_val)
    else:
        return "ニュートラルです。\nScore: " + str(pol_val)

def textapi_response(text):
    apikey = '**********************'   #自身のAPIキー
    client = pya3rt.TextClassificationClient(apikey)
    response = client.classify(text)

    return response['classes'][0]['label']

if __name__ == "__main__":
    app.run()
```

<br>

## 詳細
```python
@app.route("/callback", methods=['POST'])
def callback():

    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'
```
X-Line-Signatureリクエストヘッダーをテキスト形式で取得し、webhookを操作する。
***

```python
@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
    push_text = event.message.text
    reply_text1 = textapi_response(push_text)
    reply_text2 = judge_polarity(push_text)
    messages = [
        TextSendMessage(text=reply_text1),
        TextSendMessage(text=reply_text2),
    ]

    line_bot_api.reply_message(event.reply_token, messages)
```
Line上で返すテキストメッセージを定義する。
***

```python
dict_polarity = {}
with open('./polarity.txt', 'r') as f:
    line = f.read()
    lines = line.split('\n')
    for i in range(len(lines)):
        linecomponents = lines[i].split(':')
        dict_polarity[linecomponents[0]] = linecomponents[3]
```
単語感情極性対応表を取得する。
***

```python
def judge_polarity(text):
    t = Tokenizer()
    tokens = t.tokenize(text)
    pol_val = 0
    for token in tokens:
        word = token.surface
        pos = token.part_of_speech.split(',')[0]
        if word in dict_polarity:
            pol_val += float(dict_polarity[word])
            pol_val = round(pol_val, 5)

    if pol_val > 0.3:
        return "ポジティブです。\nScore: " + str(pol_val)
    elif pol_val < -0.3:
        return "ネガティブです。\nScore: " + str(pol_val)
    else:
        return "ニュートラルです。\nScore: " + str(pol_val)
```
単語感情極性対応表に基づいてネガポジ判定をする関数を定義する。
***

```python
def textapi_response(text):
    apikey = '**********************'   #自身のAPIキー
    client = pya3rt.TextClassificationClient(apikey)
    response = client.classify(text)

    return response['classes'][0]['label']
```
Text Classification APIを用いてトピック推定をする関数を定義する。
***

```python
if __name__ == "__main__":
    app.run()
```
サーバーの立ち上げを行う。
***

<br>

##  動作イメージ
<img src="https://user-images.githubusercontent.com/50686226/71962790-986e9800-323d-11ea-8a8a-64e123399f7e.png" width="400">
