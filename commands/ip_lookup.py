import aiohttp
import discord
from discord.ext import commands
import socket

class IpLookup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ip(self, ctx, ip_address: str):
        """Lookup OSINT avanzato su un indirizzo IP"""

        await ctx.send(f"🔍 Analisi IP in corso per: `{ip_address}`")

        url = f"http://ip-api.com/json/{ip_address}?fields=66846719"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    data = await response.json()
        except Exception as e:
            await ctx.send(f"❌ Errore durante la richiesta: `{e}`")
            return

        if data.get("status") != "success":
            await ctx.send("❌ IP non valido o impossibile da analizzare.")
            return

        # Reverse DNS
        try:
            reverse_dns = socket.gethostbyaddr(ip_address)[0]
        except:
            reverse_dns = "N/A"

        embed = discord.Embed(
            title=f"🌐 IP Lookup — {ip_address}",
            color=discord.Color.blue()
        )

        # GEO
        embed.add_field(name="🌍 Paese", value=data.get("country", "N/A"), inline=True)
        embed.add_field(name="🏙️ Regione", value=data.get("regionName", "N/A"), inline=True)
        embed.add_field(name="📍 Città", value=data.get("city", "N/A"), inline=True)
        embed.add_field(name="🛰️ Lat/Lon", value=f"{data.get('lat')}, {data.get('lon')}", inline=True)
        embed.add_field(name="⏰ Timezone", value=data.get("timezone", "N/A"), inline=True)
        embed.add_field(name="📮 ZIP", value=data.get("zip", "N/A"), inline=True)

        # NETWORK
        embed.add_field(name="🌐 ISP", value=data.get("isp", "N/A"), inline=True)
        embed.add_field(name="🏢 Organization", value=data.get("org", "N/A"), inline=True)
        embed.add_field(name="🔢 ASN", value=data.get("as", "N/A"), inline=True)
        embed.add_field(name="📡 Reverse DNS", value=reverse_dns, inline=False)

        # SECURITY
        embed.add_field(name="🛡️ Proxy", value=str(data.get("proxy", False)), inline=True)
        embed.add_field(name="🕵️ VPN", value=str(data.get("vpn", False)), inline=True)
        embed.add_field(name="🌐 Hosting", value=str(data.get("hosting", False)), inline=True)

        embed.set_footer(text="Powered by ip-api.com — OSINT IP Lookup PRO")

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(IpLookup(bot))