import discord
from discord.ext import commands
import subprocess
import requests
import os
import sys
import time

TOKEN = sys.argv[1]
ACTIVE_CHANNEL = sys.argv[2]
VTEXT_KEY = sys.argv[3]

bot = commands.Bot(command_prefix='>')
talker = 'hikari'
lines = []
flagvt = False

@bot.command()
async def join(ctx):
    print('join')
    if ctx.voice_client is None:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
            VoiceText(ctx.voice_client, 'CodeTokerが参加しました')
        else:
            await ctx.send("You are not connected to a voice channel.")

@bot.command()
async def bye(ctx):
    print('leave')
    await ctx.voice_client.disconnect()

@bot.command()
async def stop(ctx):
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()

@bot.command()
async def server_stop(ctx):
    if ctx.voice_client:
        ctx.voice_client.disconnect()
    sys.exit()

@bot.command()
async def change(ctx, message):
    global talker
    if message == 'hikari':
        talker = 'hikari'
    elif message == 'takeru':
        talker = 'takeru'
    elif message == 'show':
        talker = 'show'
    elif message == 'haruka':
        talker = 'haruka'
    else:
        VoiceText(ctx.voice_client, message + 'という声はありません')
        return
    VoiceText(ctx.voice_client, message + 'の声に変わりました')

@bot.event
async def on_ready():
    print('ready!')

@bot.event
async def on_message(message):
    print('on_message')
    if message.author.bot:
        pass
    elif message.content.startswith('>'):
        await bot.process_commands(message)
    elif message.channel.id == int(ACTIVE_CHANNEL):
        if message.guild.voice_client:
            VoiceText(message.guild.voice_client, message.content)

def VoiceText(voice_client, message=None):
    global talker
    global lines
    global flagvt
    if flagvt is True:
        print('stack')
        lines.append(message)
    elif message is None:
        if lines:
            print('pop')
            VoiceText(voice_client, lines.pop())
    else:
        flagvt = True
        print('speak')
        data = {
            'text': message,
            'speaker': talker
        }

        response = requests.post('https://api.voicetext.jp/v1/tts', data=data, auth=(VTEXT_KEY, ''))
        f = open("vtext.wav", 'wb')
        f.write(response.content)
        f.close()
        source = discord.FFmpegPCMAudio("vtext.wav")
        voice_client.play(source)
        print('played')
        while voice_client.is_playing():
            time.sleep(0.5)
        flagvt = False
        VoiceText(voice_client)

bot.run(TOKEN)
