import discord
from discord.ext import commands
import subprocess
import requests
import os
import sys
import asyncio
import traceback

INITIAL_EXTENSIONS = [
    'cogs.codetokercog'
]

TOKEN = sys.argv[1]
VTEXT_KEY = sys.argv[2]

class Codetoker(commands.Bot):
    def __init__(self, command_prefix):
        super().__init__(command_prefix)
        self.talker = 'hikari'
        self.talker_list = [
            "hikari",
            "haruka",
            "takeru",
            "show"
        ]
        self.lines = []
        self.task = None
        self.active_channel = []
        self.active_player = []

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
        elif message.channel.id in self.active_channel and message.author.id in self.active_player:
            if message.guild.voice_client.is_connected():
                if self.task is None or self.task.done():
                    self.task = asyncio.create_task( self.speak(message.guild.voice_client, message.content) )
                else:
                    self.lines.append(message.content)

    async def speak(self, voice_client, message):
        data = {
            'text': message,
            'speaker': self.talker
        }

        response = requests.post('https://api.VoiceText.jp/v1/tts', data=data, auth=(VTEXT_KEY, ''))
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
bot.run(TOKEN)
