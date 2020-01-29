from discord.ext import commands
import sys
import pickle


class CodetokerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def invite(self, ctx):
        print('invite')
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
        print('see you')
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
        if self.bot.redis.sismember("active_channels", ctx.channel.id) == 1:
            await ctx.send("既にこのチャンネルの声代理を務めています")
        else:
            self.bot.redis.sadd("active_channels", ctx.channel.id)
            await ctx.send("このチャンネルの声代理を務めます")

    @commands.command()
    async def inactivate(self, ctx):
        print('inactivate')
        if self.bot.redis.sismember("active_channels", ctx.channel.id) == 1:
            self.bot.redis.srem("active_channels", ctx.channel.id)
            await ctx.send("このチャンネルの声代理を務めないようにします")
        else:
            await ctx.send("既にこのチャンネルの声代理は務めていません")

    @commands.command()
    async def join(self, ctx):
        print('join')
        if self.bot.redis.hexists("active_users", ctx.author.id) == 1:
            await ctx.send("既にあなたの声代理を務めています")
        else:
            self.bot.redis.hsetnx("active_users", ctx.author.id, pickle.dumps({
                'pitch': 100,
                'speed': 100,
                'volume': 100
            }, protocol=pickle.HIGHEST_PROTOCOL))
            await ctx.send("あなたの声代理を務めます")

    @commands.command()
    async def bye(self, ctx):
        print('bye')
        if self.bot.redis.hexists("active_users", ctx.author.id) == 1:
            self.bot.redis.hdel("active_users", ctx.author.id)
            await ctx.send("あなたの声代理を務めないようにします")
        else:
            await ctx.send("既にあなたの声代理は務めていません")

    @commands.command()
    async def speed(self, ctx, value=100):
        print('speed')
        if self.bot.redis.hexists("active_users", ctx.author.id) == 0:
            await ctx.send("先にjoinコマンドで参加してください")
        elif value >= 50 and value <= 200:
            data = pickle.loads(self.bot.redis.hget(
                "active_users", ctx.author.id))
            data['speed'] = value
            self.bot.redis.hset("active_users", ctx.author.id, pickle.dumps(
                data, protocol=pickle.HIGHEST_PROTOCOL))
            await ctx.send("声の速さを" + str(value) + "%に設定しました")
        else:
            await ctx.send("その値は設定できません")

    @commands.command()
    async def volume(self, ctx, value=100):
        print('volume')
        if self.bot.redis.hexists("active_users", ctx.author.id) == 0:
            await ctx.send("先にjoinコマンドで参加してください")
        elif value >= 50 and value <= 200:
            data = pickle.loads(self.bot.redis.hget(
                "active_users", ctx.author.id))
            data['volume'] = value
            self.bot.redis.hset("active_users", ctx.author.id, pickle.dumps(
                data, protocol=pickle.HIGHEST_PROTOCOL))
            await ctx.send("声の大きさを" + str(value) + "%に設定しました")
        else:
            await ctx.send("その値は設定できません")

    @commands.command()
    async def pitch(self, ctx, value=100):
        print('pitch')
        if self.bot.redis.hexists("active_users", ctx.author.id) == 0:
            await ctx.send("先にjoinコマンドで参加してください")
        elif value >= 50 and value <= 200:
            data = pickle.loads(self.bot.redis.hget(
                "active_users", ctx.author.id))
            data['pitch'] = value
            self.bot.redis.hset("active_users", ctx.author.id, pickle.dumps(
                data, protocol=pickle.HIGHEST_PROTOCOL))
            await ctx.send("声のピッチを" + str(value) + "%に設定しました")
        else:
            await ctx.send("その値は設定できません")

    @commands.command()
    async def dontr(self, ctx, message=None):
        pass


def setup(bot):
    bot.add_cog(CodetokerCog(bot))
