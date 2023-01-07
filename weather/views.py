from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import *

import logging
import json
import requests

logger = logging.getLogger('django')
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)
cities = ['基隆市', '嘉義市', '臺北市', '嘉義縣', '新北市', '臺南市', '桃園縣', '高雄市', '新竹市', '屏東縣',
          '新竹縣', '臺東縣', '苗栗縣', '花蓮縣', '臺中市', '宜蘭縣', '彰化縣', '澎湖縣', '南投縣', '金門縣', '雲林縣', '連江縣']
# Create your views here.
# ngrok config add-authtoken 2JapAZA8dxnS1mRFXWxCpD6ZIN2_5DUeLnsjiuEGvP5BeHUot


@csrf_exempt
def callback(request):
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
        logger.info('Run callback function')
        logger.info(body)

        try:
            events = parser.parse(body, signature)  # 傳入的事件
            handle_message(events)
            print(HttpResponse())
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()
        return HttpResponse()
    else:
        return HttpResponseBadRequest()


def handle_message(events):
    logger.info('Run handle_message function')
    logger.info(events)
    for event in events:
        if isinstance(event, MessageEvent):
            message_location = event.message.address
            reply_token = event.reply_token
            message_type = event.message.type
            if (message_type == 'location'):
                logger.info('match Weather with current location')
                Weather_with_location(message_location, reply_token)
            else:
                message = event.message.text
                match message:
                    case "123":
                        logger.info('match 123')
                        FlexMessage = json.load(
                            open('weather\json\example.json', 'r', encoding='utf-8'))
                        line_bot_api.reply_message(
                            reply_token, FlexSendMessage(
                                'profile', FlexMessage)
                        )
                    case "456":
                        logger.info(event.message.type)
                        line_bot_api.reply_message(
                            reply_token, buttons_template_message
                        )
                    case _:
                        logger.info('No revelant response')
                        line_bot_api.reply_message(
                            reply_token, TextSendMessage(text='沒有這個指令')
                        )
                if message[:2] == "天氣":
                    logger.info('match Weather')
                    Weather_2(message, reply_token)


def Get_weather_info(city):
    token = 'CWB-B263AE2A-FD0C-4A62-9D1F-35B8590E583B'
    url = 'https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=' + \
        token + '&format=JSON&locationName=' + str(city)
    Data = requests.get(url)
    Data = (json.loads(Data.text)
            )['records']['location'][0]['weatherElement']
    logger.info(Data)
    res = [[], [], []]
    for j in range(3):
        for i in Data:
            res[j].append(i['time'][j])
    logger.info(res)
    if res[0][0]['startTime'][11:-3] == "18:00":
        starttime = "傍晚"
        endtime = "清晨"
    else:
        starttime = "清晨"
        endtime = "傍晚"
    logger.info(res)
    return res, starttime, endtime


def Get_weather_info_2(city):
    token = 'CWB-B263AE2A-FD0C-4A62-9D1F-35B8590E583B'
    url = 'https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=' + \
        token + '&format=JSON&locationName=' + str(city)
    Data = requests.get(url)
    Data = (json.loads(Data.text))['records']['location'][0]['weatherElement']
    weather_msg = json.load(
        open('weather\json\Temp.json', 'r', encoding='utf-8'))
    logger.info(Data)
    logger.info(weather_msg)
    for j in range(3):
        bubble = json.load(
            open('weather\json\Template_weather_info.json', 'r', encoding='utf-8'))

        # title
        bubble['body']['contents'][0]['text'] = city + '未來 36 小時天氣'
        # time
        bubble['body']['contents'][1]['contents'][0]['text'] = '{} ~ {}'.format(
            Data[0]['time'][j]['startTime'][5:-3], Data[0]['time'][j]['endTime'][5:-3])
        # weather
        bubble['body']['contents'][3]['contents'][1]['contents'][1]['text'] = Data[0]['time'][j]['parameter']['parameterName']
        # temp
        bubble['body']['contents'][3]['contents'][2]['contents'][1]['text'] = '{}°C ~ {}°C'.format(
            Data[2]['time'][j]['parameter']['parameterName'], Data[4]['time'][j]['parameter']['parameterName'])
        # rain
        bubble['body']['contents'][3]['contents'][1]['contents'][1]['text'] = '{}%'.format(
            Data[1]['time'][j]['parameter']['parameterName'])
        # comfort
        bubble['body']['contents'][3]['contents'][3]['contents'][1]['text'] = Data[3]['time'][j]['parameter']['parameterName']

        weather_msg['contents'].append(bubble)
        logger.info(weather_msg)
    return weather_msg


def Weather_with_location(message_location, reply_token):
    city = message_location[5:8].replace('台', '臺')
    logger.info(city)
    weather_msg = Get_weather_info_2(city)
    line_bot_api.reply_message(
        reply_token, FlexSendMessage(city + '未來 36 小時天氣預測', weather_msg))


def Weather_2(message, reply_token):
    city = message[3:]
    city = city.replace('台', '臺')
    logger.info(city)
    if (not (city in cities)):
        line_bot_api.reply_message(
            reply_token, TextSendMessage(text="查詢格式為: 天氣 縣市"))
    else:
        weather_msg = Get_weather_info_2(city)
        logger.info(weather_msg)
        line_bot_api.reply_message(
            reply_token, FlexSendMessage(city + '未來 36 小時天氣預測', weather_msg))


def Weather(message, reply_token):
    city = message[3:]
    city = city.replace('台', '臺')
    logger.info(city)
    if (not (city in cities)):
        line_bot_api.reply_message(
            reply_token, TextSendMessage(text="查詢格式為: 天氣 縣市"))
    else:
        res, starttime, endtime = Get_weather_info(city)
        logger.info(res)
        line_bot_api.reply_message(reply_token, TemplateSendMessage(
            alt_text=city + '未來 36 小時天氣預測',
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
                        thumbnail_image_url='https://cdn-icons-png.flaticon.com/512/2272/2272221.png',
                        imageSize='contain',
                        title='{} {} ~ {} {}'.format(
                            res[0][0]['startTime'][5:-9], starttime, res[0][0]['endTime'][5:-9], endtime),

                        text='天氣狀況 {}\n溫度 {} ~ {} °C\n降雨機率 {}'.format(
                            res[0][0]['parameter']['parameterName'], res[0][2]['parameter']['parameterName'], res[0][4]['parameter']['parameterName'], res[0][1]['parameter']['parameterName']),
                        actions=[
                            URIAction(
                                label='詳細內容',
                                uri='https://www.cwb.gov.tw/V8/C/W/County/index.html'
                            )
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url='https://cdn-icons-png.flaticon.com/512/2272/2272221.png',
                        title='{} {} ~ {} {}'.format(
                            res[1][0]['startTime'][5:-9], endtime, res[1][0]['endTime'][5:-9], starttime),

                        text='天氣狀況 {}\n溫度 {} ~ {} °C\n降雨機率 {}'.format(
                            res[1][0]['parameter']['parameterName'], res[1][2]['parameter']['parameterName'], res[1][4]['parameter']['parameterName'], res[1][1]['parameter']['parameterName']),
                        actions=[
                            URIAction(
                                label='詳細內容',
                                uri='https://www.cwb.gov.tw/V8/C/W/County/index.html'
                            )
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url='https://cdn-icons-png.flaticon.com/512/2272/2272221.png',
                        title='{} {} ~ {} {}'.format(
                            res[2][0]['startTime'][5:-9], starttime, res[2][0]['endTime'][5:-9], endtime),

                        text='天氣狀況 {}\n溫度 {} ~ {} °C\n降雨機率 {}'.format(
                            res[2][0]['parameter']['parameterName'], res[2][2]['parameter']['parameterName'], res[2][4]['parameter']['parameterName'], res[2][1]['parameter']['parameterName']),
                        actions=[
                            URIAction(
                                label='詳細內容',
                                uri='https://www.cwb.gov.tw/V8/C/W/County/index.html'
                            )
                        ]
                    ),
                ]
            )
        ))


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
