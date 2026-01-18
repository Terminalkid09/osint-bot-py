import aiohttp
import discord
from discord.ext import commands

class SubdomainFinder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def subdomains(self, ctx, domain: str):
        """Trova subdomini tramite fonti OSINT pubbliche"""

        await ctx.send(f"🔍 Ricerca subdomini per: `{domain}`")

        subdomains = set()

        # crt.sh (certificati SSL)
        try:
            url = f"https://crt.sh/?q={domain}&output=json"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        for entry in data:
                            name = entry.get("name_value", "")
                            if domain in name:
                                for s in name.split("\n"):
                                    subdomains.add(s.strip())
        except:
            pass

        # HackerTarget API
        try:
            url = f"https://api.hackertarget.com/hostsearch/?q={domain}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    text = await response.text()
                    for line in text.splitlines():
                        parts = line.split(",")
                        if len(parts) > 0 and domain in parts[0]:
                            subdomains.add(parts[0].strip())
        except:
            pass

        # AlienVault OTX
        try:
            url = f"https://otx.alienvault.com/api/v1/indicators/domain/{domain}/passive_dns"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    data = await response.json()
                    for entry in data.get("passive_dns", []):
                        host = entry.get("hostname", "")
                        if domain in host:
                            subdomains.add(host.strip())
        except:
            pass

        # Risultati
        if not subdomains:
            await ctx.send("❌ Nessun subdominio trovato.")
            return

        embed = discord.Embed(
            title=f"🕸️ Subdomain Finder — {domain}",
            description=f"Trovati **{len(subdomains)}** subdomini",
            color=discord.Color.blue()
        )

        # limite a 20
        listed = list(subdomains)[:20]
        embed.add_field(
            name="🔹 Subdomini trovati",
            value="\n".join(f"`{s}`" for s in listed),
            inline=False
        )

        if len(subdomains) > 20:
            embed.add_field(
                name="📌 Nota",
                value=f"Mostrati solo i primi 20 su {len(subdomains)} totali.",
                inline=False
            )

        embed.set_footer(text="Subdomain Finder OSINT PRO")

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(SubdomainFinder(bot))