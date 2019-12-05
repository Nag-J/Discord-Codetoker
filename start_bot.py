import discord
from discord.ext import commands
import subprocess
import requests
import signal
import os
import sys
import asyncio
import traceback
import configparser
import redis
import _pickle as pickle

INITIAL_EXTENSIONS = [
    'cogs.codetokercog'
]


class Codetoker(commands.Bot):
    def __init__(self, command_prefix):
        super().__init__(command_prefix)
        self.talker = 'hikari'
        self.talker_list = [
            "hikari",
            "haruka",
            "takeru",
            "show",
            "santa",
            "bear"
        ]
        self.lines = []
        self.task = None

        config = configparser.ConfigParser()
        config.read(os.path.dirname(os.path.abspath(__file__)) + '/config.ini')
        print('read: ' + os.path.dirname(os.path.abspath(__file__)) + '/config.ini')

        self.token = config['Keys']['bot_key']
        self.vtext_key = config['Keys']['voice_text_key']

        pool = redis.ConnectionPool(host=config['Redis']['host'], port=int(
            config['Redis']['port']), db=int(config['Redis']['number']))
        self.redis = redis.StrictRedis(connection_pool=pool)

        for cog in INITIAL_EXTENSIONS:
            try:
                self.load_extension(cog)
            except Exception:
                traceback.print_exc()

    async def on_ready(self):
        print('ready!')

    async def on_message(self, message):
        print('on_message')
        if message.author.bot:
            pass
        elif message.content.startswith('>'):
            await self.process_commands(message)
        elif self.redis.sismember('active_channels', message.channel.id) == 1:
            if self.redis.hexists('active_users', message.author.id) == 1:
                if message.guild.voice_client is not None:
                    if self.task is None or self.task.done():
                        self.task = asyncio.create_task(
                            self.speak(
                                message.guild.voice_client,
                                message.content,
                                pickle.loads(self.redis.hget(
                                    'active_users', message.author.id))
                            )
                        )
                    else:
                        self.lines.append(
                            {"user": message.author.id, "message": message.content}.copy())
                        print('append to lines')

    async def speak(self, voice_client, message, user_conf):
        data = {
            'text': message,
            'speaker': self.talker,
            'speed': str(user_conf['speed']),
            'volume': str(user_conf['volume']),
            'pitch': str(user_conf['pitch'])
        }

        response = requests.post(
            'https://api.VoiceText.jp/v1/tts', data=data, auth=(self.vtext_key, ''))
        f = open("vtext.wav", 'wb')
        f.write(response.content)
        f.close()
        source = discord.FFmpegPCMAudio("vtext.wav")
        voice_client.play(source)
        print('play')

        while voice_client.is_playing():
            await asyncio.sleep(0.1)
            print('speaking')

        if self.lines:
            print('pop lines')
            line = self.lines.pop()
            data = pickle.loads(self.redis.hget(
                "active_users", line["user"]))
            await self.speak(voice_client, line["message"], data)


bot = Codetoker(command_prefix='>')

loop = asyncio.get_event_loop()


def sigterm_handler(signum, frame):
    print('sigterm')
    sys.exit()


signal.signal(signal.SIGTERM, sigterm_handler)

try:
    loop.run_until_complete(bot.start(bot.token))
except KeyboardInterrupt:
    sys.exit()
finally:
    loop.run_until_complete(bot.close())
    loop.close()
    print('kill')
