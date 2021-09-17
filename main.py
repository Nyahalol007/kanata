from ext import config

import discord
from discord.ext import commands
from discord.utils import get

import os
import asyncio
import requests
import youtube_dl

from cmyui import log, Ansi
from saucenao_api import SauceNao

from pydub import AudioSegment

import math
import numpy as np

sauce = SauceNao(api_key=config.nao_key)

client = commands.Bot(command_prefix='!', help_command=None)

log('Connecting to Discord server', Ansi.GRAY)

@client.event
async def on_ready():
    activity = discord.Game(name='!help | By Gusbell', type=3)
    await client.change_presence(status=discord.Status.online, activity=activity)
    log('This bot has started ⚡️', Ansi.GREEN)

@client.command()
async def help(ctx):
    await ctx.send('```!play [name], !boost [url], !pause, !resume, !stop, !leave \n\n!boost ใส่ได้แค่ url เพลงนะคะ ใส่ชื่อเพลงไม่ได้เพราะ Gusbell ขี้เกียจค่ะ \n\nอยากได้วาร์ปรูป พิม "!warp" พร้อมแนบรูป \n\nเจ้าของ >>> https://github.com/Gusb3ll```')

@client.command()
async def play(ctx, name :str):
    check = os.path.isfile(f'{ctx.guild.id}.mp3')
    channel = ctx.author.voice.channel
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{ctx.guild.id}.mp3'
    }

    try:
        if check:
            os.remove(f'{ctx.guild.id}.mp3')
    except:
        await ctx.send('รอเพลงที่กำลังเล่นอยู่จบก่อนไม่ก็พิม !stop ค่ะ')

    try:
        await channel.connect()
    except:
        pass

    voice = get(client.voice_clients, guild=ctx.guild)
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            requests.get(name) 
        except:
            ydl.extract_info(f"ytsearch:{name}", download=True)['entries'][0]
        else:
            ydl.extract_info(name, download=True)
    voice.play(discord.FFmpegPCMAudio(f'{ctx.guild.id}.mp3'))

@client.command()
async def pause(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send('ตอนนี้ไม่มีเพลงที่กำลังเล่นอยู่ค่ะ')

@client.command()
async def resume(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send('เพลงกำลังเล่นอยู่แล้วค่ะ')

@client.command()
async def stop(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)
    voice.stop()

@client.command()
async def leave(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)
    try:
        await voice.disconnect()
    except:
        await ctx.send('ตอนนี้ไม่ได้เข้าห้องไหนอยู่นะคะ คนพิมมั่วแล้วค่ะ')

@client.command()
async def boost(ctx, url :str):
    check = os.path.isfile(f'{ctx.guild.id}.mp3')
    check2 = os.path.isfile(f'{ctx.guild.id}-boost.mp3')
    channel = ctx.author.voice.channel
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    def bass_line_freq(track):
        sample_track = list(track)
        est_mean = np.mean(sample_track)
        est_std = 3 * np.std(sample_track) / (math.sqrt(2))
        bass_factor = int(round((est_std - est_mean) * 0.005))
        return bass_factor

    try:
        if check:
            os.remove(f'{ctx.guild.id}.mp3')
        if check2:
            os.remove(f'{ctx.guild.id}-boost.mp3')
    except:
        await ctx.send('รอเพลงที่กำลังเล่นอยู่จบก่อนไม่ก็พิม !stop ค่ะ')

    try:
        await channel.connect()
    except:
        pass
    
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    for file in os.listdir('./'):
        if file.endswith('.mp3'):
            os.rename(file, f'{ctx.guild.id}.mp3')

    attenuate_db = 0
    accentuate_db = 50
    
    await ctx.send('กำลัง boost ให้ค่ะ')

    sample = AudioSegment.from_mp3(f'{ctx.guild.id}.mp3')
    filtered = sample.low_pass_filter(bass_line_freq(sample.get_array_of_samples()))

    combined = (sample - attenuate_db).overlay(filtered + accentuate_db)
    combined.export(str(ctx.guild.id) + "-boost.mp3", format="mp3")
    
    voice = get(client.voice_clients, guild=ctx.guild)

    voice.play(discord.FFmpegPCMAudio(f'{ctx.guild.id}-boost.mp3')) 

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
            title=f'ผลจากการค้นหา | มี {len(e)} วาร์ป', color=0xa5fe9f)
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

client.run(config.token)
