import discord
from discord.ext import commands
import subprocess
import requests
import os
import sys
import asyncio
import traceback
import configparser
import redis

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
        self.speed = 100
        self.volume = 100
        self.pitch = 100
        self.lines = []
        self.task = None

        config = configparser.ConfigParser()
        config.read(os.path.dirname(os.path.abspath(__file__)) + '/config.ini')
        print('read: ' + os.path.dirname(os.path.abspath(__file__)) + '/config.ini')

        self.token = config['Keys']['bot_key']
        self.vtext_key = config['Keys']['voice_text_key']
        
        pool = redis.ConnectionPool(host = config['Redis']['host'], port = int(config['Redis']['port']), db = int(config['Redis']['number']) )
        self.redis = redis.StrictRedis(connection_pool = pool)

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
        elif self.redis.sismember('active_channels', message.channel.id) == 1 and self.redis.sismember('active_users', message.author.id):
            if message.guild.voice_client.is_connected():
                if self.task is None or self.task.done():
                    self.task = asyncio.create_task( self.speak(message.guild.voice_client, message.content) )
                else:
                    self.lines.append(message.content)

    async def speak(self, voice_client, message):
        data = {
            'text': message,
            'speaker': self.talker,
            'speed': str(self.speed),
            'volume': str(self.volume),
            'pitch': str(self.pitch)
        }

        response = requests.post('https://api.VoiceText.jp/v1/tts', data=data, auth=(self.vtext_key, ''))
        f = open("vtext.wav", 'wb')
        f.write(response.content)
        f.close()
        source = discord.FFmpegPCMAudio("vtext.wav")
        voice_client.play(source)
        print('played')
        while voice_client.is_playing():
            await asyncio.sleep(0.3)
        if self.lines:
            await self.speak(voice_client, self.lines.pop())
                
bot = Codetoker(command_prefix='>')
bot.run(bot.token)
