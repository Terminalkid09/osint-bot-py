import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv
import logging
import sys

# Forza stdout a flush immediato
sys.stdout.reconfigure(line_buffering=True)

# Logging completo
logging.basicConfig(level=logging.INFO, force=True)

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot online come {bot.user}", flush=True)

async def load_extensions():
    extensions = [
        "commands.ip_lookup",
        "commands.domain_lookup",
        "commands.headers_scan",
        "commands.phone_lookup",
        "commands.social_scan",
        "commands.portscan",
        "commands.whois_lookup",
        "commands.dns_lookup",
        "commands.subdomain_finder",
        "commands.email_osint",
    ]

    for ext in extensions:
        try:
            await bot.load_extension(ext)
            print(f"[OK] Loaded {ext}", flush=True)
        except Exception as e:
            print(f"[ERRORE] Impossibile caricare {ext}: {e}", flush=True)

async def main():
    async with bot:
        await load_extensions()
        await bot.start(token)

try:
    asyncio.run(main())
except Exception as e:
    print("ERRORE CRITICO:", e, flush=True)