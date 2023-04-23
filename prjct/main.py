import datetime
import time
import sqlite3
import discord
from discord.ext import commands
import random
import logging
from discord.utils import get
from googleapiclient.discovery import build
from discord.ext import tasks

muted = []
moderation = 'off'

conn = sqlite3.connect('badwords.sqlite')
cursor = conn.cursor()
cursor.execute("SELECT word FROM words")
results = cursor.fetchall()
badwords = [str(*i) for i in results]
conn.close()

with open('moder.txt', 'r', encoding='utf8') as a:
    data = a.readline()
    moderation = data

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents.all())


@bot.command(help='Присылает изображение по данному слову.')
async def find(ctx, args):
    resource = build("customsearch", "v1", developerKey='AIzaSyDlU_AMRIDKeARiouMCD3BSQYFce6qjNtE').cse()
    result = resource.list(q=f"{args}", cx="d4daea760a8e84e4e", searchType="image").execute()
    url = result["items"][random.randint(0, 9)]["link"]
    await ctx.send(url)


@bot.command(help='Очищает канал.')
async def clear(ctx, args=''):
    if args != '' and args.isdigit():
        await ctx.channel.purge(limit=int(args))
    elif args == '':
        await ctx.channel.purge()


@bot.command(help='Создает текстовый канал с заданным именем.')
async def createtxt(ctx, args='1'):
    await ctx.guild.create_text_channel(args)


@bot.command(help='Создает голосовой канал с заданным именем.')
async def createvcv(ctx, args='1'):
    await ctx.guild.create_voice_channel(args)


@bot.command(help='Удаляет элемент с данным именем.')
async def delete(ctx, args='1'):
    channel = discord.utils.get(ctx.guild.channels, name=args)
    if channel:
        await channel.delete()


@bot.command(help='Создает категорию с заданным именем.')
async def createcat(ctx, args='1'):
    await ctx.guild.create_category(args)


@bot.command(help='Перемещает объект между категориями.')
async def move(ctx, chanel='1', categ='1'):
    channel = discord.utils.get(ctx.guild.channels, name=chanel)
    category = discord.utils.get(ctx.guild.channels, name=categ)
    await channel.edit(category=category)


@bot.command(help='Включает или выключает модерацию каналов.')
async def moderation(ctx, arg='None'):
    global moderation
    if arg == 'off':
        moderation = 'off'
        with open('moder.txt', 'w', encoding='utf8') as a:
            a.write('off')
    elif arg == 'on':
        moderation = 'on'
        with open('moder.txt', 'w', encoding='utf8') as a:
            a.write('on')
    await ctx.channel.send(f'Статус модерации: {moderation}')


@bot.event
async def on_message(message):
    global muted
    if message.author.bot:
        return
    else:
        text = message.content
        if text[0] == '!':
            await bot.process_commands(message)
        else:
            if moderation == 'on':
                rtext = text.lower().replace(' ', '')
                for j in badwords:
                    if j in rtext:
                        user = message.author
                        role = get(message.guild.roles, name='Muted')
                        await user.add_roles(role)
                        muted.append((user, role, 10))
                        await message.channel.purge(limit=1)
                        removemute.start()
                        break


@tasks.loop(minutes=1)
async def removemute():
    for i in muted:
        await i[0].remove_roles(i[1])


@removemute.before_loop
async def waiter():
    await bot.wait_until_ready()


TOKEN = ""

bot.run(TOKEN)
