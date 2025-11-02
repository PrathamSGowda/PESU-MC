import os
import asyncio
import discord
from discord.ext import commands, tasks
from mcstatus import JavaServer
from dotenv import load_dotenv
from datetime import datetime

import requests

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
SERVER_IP = os.getenv('SERVER_IP')
ADMIN_ID = [1406977396908888116,1406926755117269073,1417904819993317406,1429712625851170956,1407903342729887794,1429718356839239721]
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
    await ctx.reply("pong")

def is_admin(ctx):
    return any(role.id in ADMIN_ID for role in ctx.author.roles)

@bot.command()
async def start(ctx):
    if not is_admin(ctx):
        await ctx.reply("You can’t use this command!")
        return
    await ctx.reply("Starting Minecraft server")

@bot.command()
async def stop(ctx):
    if not is_admin(ctx):
        await ctx.reply("You can’t use this command!")
        return
    await ctx.reply("Stopping Minecraft server")

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

    #pigeon addition - sending the command to crafty
    mc_server = requests.post("https://pesu-mc.ddns.net/api/v2/servers/1/action/stop_server")

bot.run(BOT_TOKEN)
