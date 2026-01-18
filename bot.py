import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv  

load_dotenv() 
token = os.getenv("DISCORD_TOKEN") 

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot online come {bot.user}")

async def load_extensions():
    await bot.load_extension("commands.ip_lookup")
    await bot.load_extension("commands.domain_lookup")
    await bot.load_extension("commands.breach_check")
    await bot.load_extension("commands.headers_scan")
    await bot.load_extension("commands.phone_lookup")
    await bot.load_extension("commands.social_scan")
    await bot.load_extension("commands.portscan")
    await bot.load_extension("commands.whois_lookup")
    await bot.load_extension("commands.dns_lookup")
    await bot.load_extension("commands.subdomain_finder")
    await bot.load_extension("commands.email_osint")

async def main():
    async with bot:
        await load_extensions()
        await bot.start(token)

asyncio.run(main())