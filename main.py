import discord
import config
import time
from discord.ext import commands
from cmyui import log, Ansi
from saucenao_api import SauceNao

sauce = SauceNao(api_key=config.nao_key)
bot = commands.Bot(command_prefix='~')

log('Connecting to Discord server', Ansi.GRAY)

@bot.event
async def on_message(message):
    if message.content in ['วาป', 'ขอวาปหน่อย', 'อยากได้วาป', 'วาปหน่อย']:
        if message.attachments:
            f = await message.channel.send(f'{message.author.mention} กำลังหาให้อยู่')
            res = sauce.from_url(message.attachments[0].url)
            await f.delete()
            e = []

            for i in res:
                if i.urls and i.similarity > 70:
                    e.append(i)

            embed = discord.Embed(title=f"ผลจากการค้นหา | มี {len(e)} วาป", color=0xa5fe9f)
            embed.set_author(name=f"วาปของ {message.author}", icon_url=message.author.avatar_url)
            embed.set_thumbnail(url="https://i.imgur.com/hL5poNS.gif")
            for i in res:
                if i.urls and i.similarity > 70:
                    embed.add_field(name=f"[{i.author}] {i.title} | ✅ {i.similarity}%", value=f"{i.urls[0]}", inline=False)
            embed.set_footer(text="ได้แล้วก็เก็บไว้ด้วยไอ่เหี้ย เสียทรัพยากรเซิฟกูไอ่สัส")
            
            if not e:
                return await message.channel.send(f"{message.author.mention} หาวาปไม่เจอ โชคร้ายหน่อยนะไอ่โง่ หาเอาเอง 555555555555555555555")
            
            return await message.channel.send(embed=embed)

@bot.event
async def on_ready():
    log('This bot has started ⚡️', Ansi.GREEN)

bot.run(config.token)