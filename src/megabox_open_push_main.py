import discord
import queue
import time
import atexit
import multiprocessing
from logging.handlers import RotatingFileHandler
from discord.ext import tasks

from megabox_open_push_dolby_cinema import dolby_cinema_main
from megabox_open_push_function import *
from megabox_open_push_global_variable import *

# 디스코드 봇
intents = discord.Intents.default()
client = discord.Client(intents=intents)
message_queue = multiprocessing.Queue()

# 봇이 로그인하면 LOG 채널에 메세지 전송
@client.event
async def on_ready():
    # 봇이 오프라인에서 온라인으로 바뀌었을 때 1회 시작됨
    channel_id = discord_channel_id_dictionary["LOG"]
    channel = client.get_channel(channel_id)
    await channel.send('megabox-open-push-discord-bot connected...')

    # 메시지를 주기적으로 보내는 send_message 루프 시작.
    await send_message.start()


# 데코레이터는 discord.ext.tasks 모듈의 기능으로, 비동기 함수(async def)를 일정 주기로 반복 실행
@tasks.loop(seconds=1)
async def send_message():

    if not message_queue.empty():
        message = message_queue.get(0)
        channel_id = discord_channel_id_dictionary.get(message[0])
        print(f"send_message to {message[0]} : {message[1]}, channel_id : {channel_id}")
        
        if channel_id:
            channel = client.get_channel(channel_id)

            await channel.send(message[1])

# 프로세스 배열
processes = []

# handlers = [RotatingFileHandler('megabox-open-push.log', maxBytes=5*1024*1024, backupCount=3, encoding='utf-8')]
# logging.basicConfig(handlers=handlers, level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')


# megabox_open_push_status.py 실행
if __name__ == '__main__':

    # 서버 시작 알림 보내기
    message_queue.put(["LOG", "megabox-open-push server started..."])


    for data in enumerate(dolby_cinema_json_data):
        p = multiprocessing.Process(target=dolby_cinema_main, args=(dolby_cinema_url, dolby_cinema_cookies, dolby_cinema_headers, data[1], dolby_cinema_target_name[data[0]], message_queue))
        processes.append(p)
        p.start()
        time.sleep(1)


    # if dolby_cinema_json_data:
    #     dolby_cinema_main(dolby_cinema_url, dolby_cinema_cookies, dolby_cinema_headers, dolby_cinema_json_data[0], dolby_cinema_target_name[0], message_queue)
    
    # 종료 시 서버 종료 알림 보내기
    def send_stopped_message():
        message_queue.put(["LOG", "megabox-open-push server stopped..."])
        
    # 프로그램 종료될때 자동 실행
    atexit.register(send_stopped_message)

    client.run(discord_bot_token)