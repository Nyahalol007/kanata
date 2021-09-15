import os
import discord
import youtube_dl
import asyncio
from ext import config
from discord.ext import commands
from cmyui import log, Ansi
from saucenao_api import SauceNao

sauce = SauceNao(api_key=config.nao_key)

client = commands.Bot(command_prefix='!', help_command=None)

log('Connecting to Discord server', Ansi.GRAY)

@client.command()
async def help(ctx):
    await ctx.send('```!play [url], !pause, !resume, !stop, !leave \n\n!play มีใส่ได้แค่ url เพลงนะคะ ใส่ชื่อเพลงไม่ได้เพราะ Gusbell ขี้เกียจค่ะ \n\nอยากได้วาร์ปรูป พิม "!warp" พร้อมแนบรูป \n\nเจ้าของ >>> https://github.com/Gusb3ll```')

@client.command()
async def play(ctx, url: str):
    song_there = os.path.isfile('song.mp3')
    try:
        if song_there:
            os.remove('song.mp3')
    except PermissionError:
        await ctx.send('รอเพลงที่กำลังเล่นอยู่จบก่อนไม่ก็พิม !stop ค่ะ')
        return

    voiceChannel = discord.utils.get(ctx.guild.voice_channels, name='General')
    await voiceChannel.connect()
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    for file in os.listdir('./'):
        if file.endswith('.mp3'):
            os.rename(file, 'song.mp3')
    await ctx.send('กำลังเปิดเพลงให้ค่ะ โปรดรอสักครู่')
    voice.play(discord.FFmpegPCMAudio('song.mp3'))

@client.command()
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        await ctx.send('กำลังหยุดให้ค่ะ')
        voice.pause()
    else:
        await ctx.send('ตอนนี้ไม่มีเพลงที่กำลังเล่นอยู่ค่ะ')

@client.command()
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        await ctx.send('กำลังเริ่มเล่นให้ค่ะ')
        voice.resume()
    else:
        await ctx.send('เพลงกำลังเล่นอยู่แล้วค่ะ')

@client.command()
async def stop(ctx):
    await ctx.send('กำลังหยุดให้ค่ะ')
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    voice.stop()

@client.command()
async def leave(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_connected():
        await ctx.send('bye bye ค่าาา')
        await voice.disconnect()
    else:
        await ctx.send('ตอนนี้ไม่ได้เข้าห้องไหนอยู่นะคะ คนพิมมั่วแล้วค่ะ')

@client.command()
async def warp(ctx):
    await ctx.send('ส่งรูปด้วยค่ะ')

    def check(message):
        attachments = message.attachments
        if len(attachments) == 0:
            return False
        attachment = attachments[0]
        return attachment.filename.endswith(('.jpg', '.png'))

    msg = await client.wait_for('message', check=check)
    image = msg.attachments[0]

    if image:
        t = await ctx.send(f'{ctx.author.mention} กำลังหาให้อยู่นะคะ')
        res = sauce.from_url(image.url)
        await t.delete()
        e = []
        for i in res:
            if i.urls and i.similarity > 70:
                e.append(i)
        embed = discord.Embed(
            title=f'ผลจากการค้นหา | มี {len(e)} วาป', color=0xa5fe9f)
        embed.set_author(
            name=f'วาปของ {ctx.author}', icon_url=ctx.author.avatar_url)
        for i in res:
            if i.urls and i.similarity > 70:
                embed.add_field(
                    name=f'[{i.author}] {i.title} | ✅ {i.similarity}%', value=f'{i.urls[0]}', inline=False)
        embed.set_footer(text='ได้แล้วก็เก็บไว้ด้วยค่ะ')

        if not e:
            return await ctx.send(f'{ctx.author.mention} หาวาปไม่เจอค่ะ สมน้ำหน้าค่ะ')

        return await ctx.send(embed=embed)
    else:
        t = await ctx.send(f'{ctx.author.mention} ไหนรูปคะ แนบรูปมาด้วยค่ะ')
        await asyncio.sleep(5)
        await t.delete()

@client.event
async def on_ready():
    activity = discord.Game(name='!help | By Gusbell', type=3)
    await client.change_presence(status=discord.Status.online, activity=activity)
    log('This bot has started ⚡️', Ansi.GREEN)

client.run(config.token)
