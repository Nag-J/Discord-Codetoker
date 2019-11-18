from discord.ext import commands
import sys

class CodetokerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def invite(self, ctx):
        print('join')
        if ctx.voice_client:
            await ctx.send("もう呼ばれてます")
        else:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
                await ctx.send("こんにちは")
            else:
                await ctx.send("Voice Channelに接続してから呼んでください")

    @commands.command()
    async def seeyou(self, ctx):
        print('leave')
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("おやすみなさい")
        else:
            await ctx.send("Voice Channelに参加していません")

    @commands.command()
    async def stop(self, ctx):
        print('stop')
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("！！")
        await ctx.send("しゃべってません")

    @commands.command()
    async def change(self, ctx, message):
        print('change')
        if message in self.bot.talker_list:
            self.bot.talker = message
            await ctx.send(message + "に変身")
        else:
            await ctx.send(message + "という声はないです")

    @commands.command()
    async def activate(self, ctx):
        print('activate')
        if ctx.channel.id in self.bot.active_channel:
            await ctx.send("既にこのチャンネルの声代理を務めています")
        else:
            self.bot.active_channel.append(ctx.channel.id)
            await ctx.send("このチャンネルの声代理を務めます")

    @commands.command()
    async def inactivate(self, ctx):
        print('inactivate')
        if ctx.channel.id in self.bot.active_channel:
            self.bot.active_channel.pop(self.bot.active_channel.index(ctx.channel.id))
            await ctx.send("このチャンネルの声代理を務めないようにします")
        else:
            await ctx.send("既にこのチャンネルの声代理は務めていません")

    @commands.command()
    async def join(self, ctx):
        if ctx.author.id in self.bot.active_player:
            await ctx.send("既にあなたの声代理を務めています")
        else:
            self.bot.active_player.append(ctx.author.id)
            await ctx.send("あなたの声代理を務めます")

    @commands.command()
    async def bye(self, ctx):
        if ctx.author.id in self.bot.active_player:
            self.bot.active_player.pop(self.bot.active_player.index(ctx.author.id))
            await ctx.send("あなたの声代理を務めないようにします")
        else:
            await ctx.send("既にあなたの声代理は務めていません")
            
    @commands.command()
    async def stats(self, ctx):
        vc = "\tNot connected\n"
        if ctx.voice_client:
            vc = "\tConnected\n"
        channels = ""
        players = ""
        for channel_id in self.bot.active_channel:
            channels += "\t" + self.bot.get_channel(channel_id).name + "\n"
        for player_id in self.bot.active_player:
            players += "\t" + self.bot.get_user(player_id).name + "\n"
        if channels == "":
            channels = "\tNone\n"
        if players == "":
            players = "\tNone\n"
        
        await ctx.send("STATS\n" +
                       "Voice channel:\n" + vc +
                       "Activated text channel(s):\n" + channels +
                       "Joined player(s):\n" + players)

    @commands.command()
    async def speed(self, ctx, value=100):
        if value >= 50 and value <= 200:
            self.bot.speed = value
            await ctx.send("声の速さを" + str(value) + "%に設定しました")
        else:
            await ctx.send("その値は設定できません")
            
    @commands.command()
    async def volume(self, ctx, value=100):
        if value >= 50 and value <= 200:
            self.bot.volume = value
            await ctx.send("声の大きさを" + str(value) + "%に設定しました")
        else:
            await ctx.send("その値は設定できません")
            
    @commands.command()
    async def pitch(self, ctx, value=100):
        if value >= 50 and value <= 200:
            self.bot.pitch = value
            await ctx.send("声のピッチを" + str(value) + "%に設定しました")
        else:
            await ctx.send("その値は設定できません")

def setup(bot):
    bot.add_cog(CodetokerCog(bot))