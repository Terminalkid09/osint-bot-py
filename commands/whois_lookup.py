import discord
from discord.ext import commands
import whois
import datetime

class WhoisLookup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def whois(self, ctx, domain: str):
        """Mostra informazioni WHOIS avanzate di un dominio"""

        await ctx.send(f"🔍 Recupero WHOIS per: `{domain}`")

        try:
            data = whois.whois(domain)
        except Exception as e:
            await ctx.send(f"❌ Errore durante la richiesta WHOIS: `{e}`")
            return

        embed = discord.Embed(
            title=f"🌐 WHOIS — {domain}",
            color=discord.Color.blue()
        )

        def safe(value):
            if isinstance(value, list):
                return ", ".join(str(v) for v in value)
            return value if value else "N/A"

        def format_date(value):
            if isinstance(value, list):
                value = value[0]
            if isinstance(value, datetime.datetime):
                return value.strftime("%Y-%m-%d %H:%M:%S")
            return "N/A"

        embed.add_field(name="📅 Creato", value=f"`{format_date(data.creation_date)}`", inline=False)
        embed.add_field(name="⏳ Scadenza", value=f"`{format_date(data.expiration_date)}`", inline=False)
        embed.add_field(name="♻️ Ultimo aggiornamento", value=f"`{format_date(data.updated_date)}`", inline=False)

        embed.add_field(name="🏢 Registrar", value=f"`{safe(data.registrar)}`", inline=False)
        embed.add_field(name="👤 Registrant", value=f"`{safe(data.get('name'))}`", inline=False)
        embed.add_field(name="🏛️ Organization", value=f"`{safe(data.get('org'))}`", inline=False)

        embed.add_field(name="🧩 Nameserver", value=f"`{safe(data.name_servers)}`", inline=False)
        embed.add_field(name="📍 Paese", value=f"`{safe(data.country)}`", inline=False)
        embed.add_field(name="📧 Email", value=f"`{safe(data.emails)}`", inline=False)

        embed.add_field(name="🔐 DNSSEC", value=f"`{safe(data.get('dnssec'))}`", inline=False)
        embed.add_field(name="📌 Status", value=f"`{safe(data.get('status'))}`", inline=False)

        embed.set_footer(text="WHOIS Lookup PRO")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(WhoisLookup(bot))