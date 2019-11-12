from discord.ext import commands
import sys

class CodetokerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx):
        print('join')
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")

    @commands.command()
    async def bye(self, ctx):
        print('leave')
        await ctx.voice_client.disconnect()

    @commands.command()
    async def stop(self, ctx):
        print('stop')
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()

    @commands.command()
    async def server_stop(self, ctx):
        print('server_stop')
        if ctx.voice_client.is_connected():
            await ctx.voice_client.disconnect()
        sys.exit()

    @commands.command()
    async def change(self, ctx, message):
        print('change')
        if message == 'hikari':
            self.bot.talker = 'hikari'
        elif message == 'takeru':
            self.bot.talker = 'takeru'
        elif message == 'show':
            self.bot.talker = 'show'
        elif message == 'haruka':
            self.bot.talker = 'haruka'

def setup(bot):
    bot.add_cog(CodetokerCog(bot))