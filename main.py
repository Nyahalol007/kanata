import os
import config
import discord
import asyncio
from cmyui import log, Ansi
from discord.ext import commands
from saucenao_api import SauceNao

client = commands.Bot(command_prefix='+', help_command=None)
sauce = SauceNao(api_key=config.nao_key)

log('Connecting to Discord server', Ansi.GRAY)

@client.event
async def on_ready():
    activity = discord.Game(name='!help', type=3)
    await client.change_presence(status=discord.Status.online, activity=activity)
    log('This bot has started ⚡️', Ansi.GREEN)

@client.command()
async def help(ctx):
    await ctx.send('```+math +warp```')

@client.command()
async def math(ctx):
    await ctx.send("บวก, ลบ, คูณ, หาร")
    msg = await client.wait_for('message')
    if msg.content == 'บวก':
        await ctx.send('เลขตัวแรก')
        a_raw = await client.wait_for('message')
        a = a_raw.content
        await ctx.send('เลขตัวที่สอง')
        b_raw = await client.wait_for('message')
        b = b_raw.content
        await ctx.send(f'มึงต้องการให้ : {a} + {b} ใช่ไหมไอสัส')
        conf = await client.wait_for('message')
        if conf.content == 'ใช่':
            calc = float(a) + float(b)
            ans = f'อะเอาไปไอสัส : {calc}'
            print(ans)
            await ctx.send(ans)
        elif conf == 'ไม่':
            pass
    elif msg.content == 'ลบ':
        await ctx.send('เลขตัวแรก')
        a_raw = await client.wait_for('message')
        a = a_raw.content
        await ctx.send('เลขตัวที่สอง')
        b_raw = await client.wait_for('message')
        b = b_raw.content
        await ctx.send(f'มึงต้องการ : {a} - {b} ใช่ไหมไอสัส')
        conf = await client.wait_for('message')
        if conf.content == 'ใช่':
            calc = float(a) - float(b)
            ans = f'อะเอาไปไอสัส : {calc}'
            print(ans)
            await ctx.send(ans)
        elif conf == 'ไม่':
            pass
    elif msg.content == 'คูณ':
        await ctx.send('เลขตัวแรก')
        a_raw = await client.wait_for('message')
        a = a_raw.content
        await ctx.send('เลขตัวที่สอง')
        b_raw = await client.wait_for('message')
        b = b_raw.content
        await ctx.send(f'มึงต้องการ : {a} * {b} ใช่ไหมไอสัส')
        conf = await client.wait_for('message')
        if conf.content == 'ใช่':
            calc = float(a) * float(b)
            ans = f'อะเอาไปไอสัส : {calc}'
            print(ans)
            await ctx.send(ans)
        elif conf == 'ไม่':
            pass
    elif msg.content == 'หาร':
        await ctx.send('เลขตัวแรก')
        a_raw = await client.wait_for('message')
        a = a_raw.content
        await ctx.send('เลขตัวที่สอง')
        b_raw = await client.wait_for('message')
        b = b_raw.content
        await ctx.send(f'มึงต้องการให้ : {a} / {b} ใช่ไหมไอสัส')
        conf = await client.wait_for('message')
        if conf.content == 'ใช่':
            calc = float(a) / float(b)
            ans = f'อะเอาไปไอสัส : {calc}'
            print(ans)
            await ctx.send(ans)
        elif conf == 'ไม่':
            pass

@client.command()
async def warp(ctx):
    await ctx.send('ส่งรูปมาดิ๊เดียวหาให้')

    def check(message):
        attachments = message.attachments
        if len(attachments) == 0:
            return False
        attachment = attachments[0]
        return attachment.filename.endswith(('.jpg', '.png'))

    msg = await client.wait_for('message', check=check)
    image = msg.attachments[0]

    if image:
        t = await ctx.send(f'{ctx.author.mention} กำลังหาให้ไอสัสรอเเปป')
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

        if not e:
            return await ctx.send(f'{ctx.author.mention} หาวาปไม่เจอ')

        return await ctx.send(embed=embed)
    else:
        t = await ctx.send(f'{ctx.author.mention} โปรดแนบรูปมา')
        await asyncio.sleep(5)
        await t.delete()

client.run(config.token)
