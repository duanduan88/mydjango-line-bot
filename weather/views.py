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
cities = ['基隆市', '嘉義市', '臺北市', '嘉義縣', '新北市', '臺南市', '桃園市', '高雄市', '新竹市', '屏東縣',
          '新竹縣', '臺東縣', '苗栗縣', '花蓮縣', '臺中市', '宜蘭縣', '彰化縣', '澎湖縣', '南投縣', '金門縣', '雲林縣', '連江縣']
date_content_18_06 = ['今晚明晨', '明日白天', '明日傍晚']
date_content_06_18 = ['今日白天', '今日傍晚', '明日白天']


@csrf_exempt
def callback(request):
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
        logger.info('Run callback function')
        logger.info(body)

        try:
            # Receive the event
            events = parser.parse(body, signature)
            handle_message(events)
            print(HttpResponse())

        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()
        return HttpResponse()
    else:
        return HttpResponseBadRequest()

# handle all message and decide to reply what sentance


def handle_message(events):
    logger.info('Run handle_message function')
    logger.info(events)
    for event in events:
        if isinstance(event, MessageEvent):
            reply_token = event.reply_token

            # Message type == location
            if (event.message.type == 'location'):
                message_location = event.message.address
                logger.info('match Weather with current location')
                Weather_search_with_location(message_location, reply_token)

            # Message type == text
            elif (event.message.type == 'text'):
                message = event.message.text
                if (message[:2] == "天氣"):
                    logger.info('match Weather')
                    Weather_search(message, reply_token)

                elif (message == "123"):
                    logger.info('match 123')
                    FlexMessage = json.load(
                        open('weather\json\example.json', 'r', encoding='utf-8'))
                    line_bot_api.reply_message(
                        reply_token, FlexSendMessage(
                            'profile', FlexMessage)
                    )
                else:
                    logger.info('No revelant response')
                    line_bot_api.reply_message(
                        reply_token, TextSendMessage(text='沒有這個指令')
                    )


'''
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
'''


def Get_weather(city):
    # token from 中央氣象局
    token = 'CWB-B263AE2A-FD0C-4A62-9D1F-35B8590E583B'
    url = 'https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=' + \
        token + '&format=JSON&locationName=' + str(city)
    # Get request from url
    Data = requests.get(url)
    data_test = (json.loads(Data.text))
    logger.info(data_test)
    # Get specific data from url
    Data = (json.loads(Data.text))['records']['location'][0]['weatherElement']
    # Temp.json is blank and for adding the data in it
    weather_msg = json.load(
        open('weather\json\Temp.json', 'r', encoding='utf-8'))
    logger.info(Data)
    logger.info(weather_msg)

    # Catch weather info of 3 timing, e.g. 18:00-06:00
    for j in range(3):
        template = json.load(
            open('weather\json\Template_weather_more_info.json', 'r', encoding='utf-8'))

        # city
        template['body']['contents'][1]['text'] = city
        # time
        # template['body']['contents'][2]['text'] = '{} ~ {}'.format(
        #     Data[0]['time'][j]['startTime'][11:-3], Data[0]['time'][j]['endTime'][11:-3]).replace('-', '/')
        # temp
        template['body']['contents'][2]['text'] = '{}°C ~ {}°C'.format(
            Data[2]['time'][j]['parameter']['parameterName'], Data[4]['time'][j]['parameter']['parameterName'])
        # weather condition
        template['body']['contents'][4]['contents'][0]['contents'][1]['text'] = '{}'.format(
            Data[0]['time'][j]['parameter']['parameterName'])
        # rain rate
        template['body']['contents'][4]['contents'][1]['contents'][1]['text'] = '{}%'.format(
            Data[1]['time'][j]['parameter']['parameterName'])
        # temp in box
        template['body']['contents'][4]['contents'][2]['contents'][1]['text'] = '{}°C ~ {}°C'.format(
            Data[2]['time'][j]['parameter']['parameterName'], Data[4]['time'][j]['parameter']['parameterName'])
        # comfortable
        template['body']['contents'][4]['contents'][3]['contents'][1]['text'] = '{}'.format(
            Data[3]['time'][j]['parameter']['parameterName'])
        # Fill all 3 info in weather_msg by using template
        weather_msg['contents'].append(template)
        logger.info(Data[0]['time'][0]['startTime'][11:])

    # See now timing and decide to display which content
    if (Data[0]['time'][0]['startTime'][11:] == "18:00:00" or Data[0]['time'][0]['startTime'][11:] == "00:00:00"):
        logger.info('Now time is 18:00 ~ 06:00')
        for i in range(3):
            weather_msg['contents'][i]['body']['contents'][0]['text'] = date_content_18_06[i]
            logger.info(weather_msg)
    else:
        logger.info('Now time is 06:00 ~ 18:00')
        for m in range(3):
            weather_msg['contents'][m]['body']['contents'][0]['text'] = date_content_06_18[m]
            logger.info(weather_msg)

    return weather_msg


def Weather_search_with_location(message_location, reply_token):
    logger.info('Run Weather_search_with_location')
    # Get location by event.message.address
    city = message_location[5:8].replace('台', '臺')
    logger.info(city)
    # Go to get weather info
    weather_msg = Get_weather(city)
    line_bot_api.reply_message(
        reply_token, FlexSendMessage(city + '未來 36 小時天氣預測', weather_msg))


def Weather_search(message, reply_token):
    logger.info('Run Weather_search')
    city = message[3:]
    city = city.replace('台', '臺')
    logger.info(city)
    # Make sure formatt is correct
    if (not (city in cities)):
        line_bot_api.reply_message(
            reply_token, TextSendMessage(text="查詢格式為: 天氣 縣市"))
    else:
        # Go to get weather info
        weather_msg = Get_weather(city)
        logger.info(weather_msg)
        line_bot_api.reply_message(
            reply_token, FlexSendMessage(city + '未來 36 小時天氣預測', weather_msg))


'''
def GetWeatherIcon():
    url = 'https://www.cwb.gov.tw/Data/js/WeatherIcon.js?_=1673188068816'
    # Get request from url
    icon_data = requests.get(url)
    data_test = (json.loads(icon_data.text))
    logger.info(data_test)
'''


'''
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
'''
'''
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
'''
