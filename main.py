import discord
import config
import asyncio
from discord.ext import commands
from cmyui import log, Ansi
from saucenao_api import SauceNao

sauce = SauceNao(api_key=config.nao_key)
bot = commands.Bot(command_prefix='=')

log('Connecting to Discord server', Ansi.GRAY)

@bot.event
async def on_message(message):
    if message.content in ['วาป', 'ขอวาป', 'warp', 'ขอวาปหน่อย', 'อยากได้วาป', 'วาปหน่อย']:
        if message.attachments:
            f = await message.channel.send(f'{message.author.mention} กำลังหาให้อยู่นะคะ')
            res = sauce.from_url(message.attachments[0].url)
            await f.delete()
            e = []

            for i in res:
                if i.urls and i.similarity > 70:
                    e.append(i)

            embed = discord.Embed(title=f'ผลจากการค้นหา | มี {len(e)} วาป', color=0xa5fe9f)
            embed.set_author(name=f'วาปของ {message.author}', icon_url=message.author.avatar_url)
            for i in res:
                if i.urls and i.similarity > 70:
                    embed.add_field(name=f'[{i.author}] {i.title} | ✅ {i.similarity}%', value=f'{i.urls[0]}', inline=False)
            embed.set_footer(text='ได้แล้วก็เก็บไว้ด้วยค่ะ')
            
            if not e:
                return await message.channel.send(f'{message.author.mention} หาวาปไม่เจอค่ะ สมน้ำหน้าคน horny ค่ะ')
            
            return await message.channel.send(embed=embed)
        else: 
            f = await message.channel.send(f'{message.author.mention} ไหนรูปคะ แนบรูปมาด้วยค่ะ')
            await asyncio.sleep(5)
            await f.delete()

@bot.event
async def on_ready():
    activity = discord.Game(name='วาป | Modified by Gusbell', type=3)
    await bot.change_presence(status=discord.Status.online, activity=activity)
    log('This bot has started ⚡️', Ansi.GREEN)

bot.run(config.token)