import discord
from discord.ext import commands, tasks
import datetime as dt

class Atsui(commands.Cog):
    #The variables for this cog are as follows:
    #    HOUR,MINUTE
    global hour, minute
    def __init__(self, bot):
        self.bot = bot
        with open('cogs/atsui/vars.txt') as f:
            variables = f.readline().split(',')
            hour = variables[0]
            minute = variables[1]
            f.close()

        print(hour + ':' + minute)

        self.atsui.start()
    
    def cog_unload(self):
        self.atsui.cancel()
    
    @commands.command(name='settime')
    async def set_time(self, ctx, hour, minute):
        await ctx.send(str(hour) + ':' + str(minute))


    @tasks.loop(time=dt.time(hour=hour, minute=minute, tzinfo=dt.timezone.utc))
    async def atsui(self):
        print('ATSUI YO')


async def setup(bot):
    await bot.add_cog(Atsui(bot))