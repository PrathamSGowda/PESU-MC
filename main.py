import os
import asyncio
import discord
from discord.ext import commands, tasks
from mcstatus import JavaServer
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
SERVER_IP = os.getenv('SERVER_IP')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='$', intents=intents)

empty_time = None
trigger_shutdown = False

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    check_server.start()

@bot.command()
async def ping(ctx):
    await ctx.send("pong")

@bot.command()
async def cat(ctx):
    await ctx.send("meow")

@bot.command()
async def pikachu(ctx):
    await ctx.send("pika pika")

@tasks.loop(seconds=1)
async def check_server():
    global empty_time, trigger_shutdown
    try:
        server = JavaServer.lookup(SERVER_IP)
        status = server.status()
        player_count = status.players.online
        print(f'Players online: {player_count}')

        if player_count == 0:
            if empty_time is None:
                empty_time = datetime.now()
            else:
                elapsed = (datetime.now() - empty_time).total_seconds()
                if elapsed >= 60 and not trigger_shutdown:
                    trigger_shutdown = True
                    await shutdown_server()
        else:
            empty_time = None
            trigger_shutdown = False
    except Exception as e:
        print(f'Error checking server status: {e}')

async def shutdown_server():
    channel = discord.utils.get(bot.get_all_channels(), name='dev-chat')
    if channel:
        await channel.send('Server has been empty for 5 minutes. Initiating shutdown sequence.')
    print('Shutting down server...')

bot.run(BOT_TOKEN)
