import os
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

line_channel_secret = "204453e222eb466da5c906575f9dc913"
line_channel_access_token = "Nfyc2vEIEARdcELDaW236jn6cDmLSGQEQw8FXuG4gBOgTfYqGC94t9lRSun0f0WInBFRYZ/r195Vk1kj3FB9XNJPpqzExQZNQK5e7++M4mYKjvgFSWmP15/nkxMCen1cZYkvgkVfFlYHyB4mhqSW+AdB04t89/1O/w1cDnyilFU="

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
    reply_text = judge_polarity(push_text)

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

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
        return "ポジティブです。¥n
         Score: " + str(pol_val)
    elif pol_val < -0.3:
        return "ネガティブです。¥n
         Score: " + str(pol_val)
    else:
        return "ニュートラルです。¥n
         Score: " + str(pol_val)

if __name__ == "__main__":
    app.run()