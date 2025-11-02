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
CRAFTY_TOKEN = os.getenv('CRAFTY_TOKEN')
SERVER_IP = os.getenv('SERVER_IP')
SERVER_ID = os.getenv('SERVER_ID')
ADMIN_ID = [int(rid.strip()) for rid in os.getenv("ADMIN_ID").split(",")]
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

@bot.command()
async def josh(ctx):
    await ctx.reply("is dumass")

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
    await shutdown_server(manual=True)

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

async def shutdown_server(manual=False):
    headers = {"Authorization": f"{CRAFTY_TOKEN}","Content-Type": "application/json"}
    channel = discord.utils.get(bot.get_all_channels(), name='dev-chat')
    if channel:
        if manual:
            await channel.send('Server stop command received from admin. Stopping Minecraft server...')
            await requests.post(f"https://pesu-mc.ddns.net:8443/api/v2/servers/{SERVER_ID}/action/stop_server", headers=headers, verify=False)
        else:
            await channel.send('Server has been empty for 5 minutes. Initiating automatic shutdown sequence.')
    print('Shutting down server...')
    

async def start_server(manual=False):
    headers = {"Authorization": f"{CRAFTY_TOKEN}","Content-Type": "application/json"}
    channel = discord.utils.get(bot.get_all_channels(), name='dev-chat')
    if channel:
        if manual:
            await channel.send('get in losers mc server is starting')
            await requests.post(f"https://pesu-mc.ddns.net:8443/api/v2/servers/{SERVER_ID}/action/start_server", headers=headers, verify=False)


bot.run(BOT_TOKEN)
