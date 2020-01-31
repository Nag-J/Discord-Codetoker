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
import wave
import re
INITIAL_EXTENSIONS = [
    'cogs.codetokercog'
]


class Codetoker(commands.Bot):
    def __init__(self, command_prefix):
        super().__init__(command_prefix)
        self.talker = 'hikari'
        self.talker_list = [
            'hikari',
            'haruka',
            'takeru',
            'show',
            'santa',
            'bear'
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
                                message,
                                pickle.loads(self.redis.hget(
                                    'active_users', message.author.id))
                            )
                        )
                    else:
                        self.lines.append(
                            {'user': message.author.id, 'message': message}.copy())
                        print('append to lines')

    async def speak(self, message, user_conf):
        speech_message = message.content
        for m in message.mentions:
            speech_message = re.sub(
                '<@!' + str(m.id) + '>', str(m.display_name), speech_message)
        speech_message = re.sub(
            r'(http|https):\/\/([\w\-]+\.)+[\w\-]+(\/[\w\-.\/?%&=]*)?', 'URL', speech_message)
        data = {
            'text': speech_message,
            'speaker': self.talker,
            'speed': str(user_conf['speed']),
            'volume': str(user_conf['volume']),
            'pitch': str(user_conf['pitch'])
        }
        response = requests.post(
            'https://api.VoiceText.jp/v1/tts', data=data, auth=(self.vtext_key, ''))
        f = open('vtext.wav', 'wb')
        f.write(response.content)
        f.close()
        source = discord.FFmpegPCMAudio('vtext.wav')
        message.guild.voice_client.play(source)
        print('play: ' + speech_message)
        wf = wave.open('vtext.wav', 'r')
        await asyncio.sleep(float(wf.getnframes()) / wf.getframerate())
        if self.lines:
            print('pop lines')
            line = self.lines.pop()
            data = pickle.loads(self.redis.hget(
                'active_users', line['user']))
            await self.speak(line['message'], data)

    async def on_voice_state_update(self, member, before, after):
        for v in self.voice_clients:
            if len(v.channel.members) == 1:
                await v.disconnect()


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
