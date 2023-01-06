from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import *

import logging
logger = logging.getLogger('django')

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)

# Create your views here.
# ngrok config add-authtoken 2JapAZA8dxnS1mRFXWxCpD6ZIN2_5DUeLnsjiuEGvP5BeHUot


def hello_world(request):
    return HttpResponse("Hello World")


@csrf_exempt
def callback(request):
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
        logger.info('Run callback function')
        logger.info(body)
        print(body)
        try:
            events = parser.parse(body, signature)  # 傳入的事件

        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()

        for event in events:
            if isinstance(event, MessageEvent):
                print(event.message.type)
                line_bot_api.reply_message(
                    event.reply_token, buttons_template_message
                )

            return HttpResponse()
    else:
        return HttpResponseBadRequest()


TemplateSendMessage(
    alt_text='Buttons template',
    template=ButtonsTemplate(
        title='Menu',
        text='請選擇地區',
        actions=[
            MessageTemplateAction(
                label='台北市',
                text='台北市'
            ),
            MessageTemplateAction(
                label='台中市',
                text='台中市'
            ),
            MessageTemplateAction(
                label='高雄市',
                text='高雄市'
            )
        ]
    )
)


buttons_template_message = TemplateSendMessage(
    alt_text='Buttons template',
    template=ButtonsTemplate(
        thumbnail_image_url='https://raw.githubusercontent.com/duanduan88/mydjango-line-bot/master/weather/photo/thumbnail_image_1.jpg',
        image_aspect_ratio='rectangle',
        image_size='contain',
        image_background_color='#FFFFFF',
        title='Menu',
        text='Please select',
        default_action=URIAction(
            label='view detail',
            uri='http://example.com/page/123'
        ),
        actions=[
            PostbackAction(
                label='postback',
                display_text='postback text',
                data='action=buy&itemid=1'
            ),
            LocationAction(
                label='location'
            ),
            DatetimePickerAction(
                label='Select date',
                data='storeId=12345',
                mode='datetime',
                initial="2018-12-25T00:00",
                min='2017-01-24T23:59',
                max='2018-12-25T00:00'
            )
        ]
    )
)
