import aiohttp
import discord
from discord.ext import commands
import socket
import whois
import ssl
import datetime

class DomainLookup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def domain(self, ctx, domain: str):
        """Analizza un dominio e mostra informazioni OSINT avanzate"""

        await ctx.send("🔍 Analisi del dominio in corso...")

        # Risoluzione dominio => IP
        try:
            ip_address = socket.gethostbyname(domain)
        except socket.gaierror:
            await ctx.send("❌ Dominio non valido o impossibile da risolvere.")
            return

        # Lookup IP con ip-api
        url = f"http://ip-api.com/json/{ip_address}?fields=66846719"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    ip_data = await response.json()
        except:
            await ctx.send("❌ Errore durante la richiesta IP-API.")
            return

        if ip_data.get("status") != "success":
            await ctx.send("❌ Impossibile ottenere informazioni sull'IP.")
            return

        # WHOIS del dominio
        try:
            w = whois.whois(domain)
            registrar = w.registrar or "N/A"
            creation = w.creation_date
            expiry = w.expiration_date

            # Gestione date multiple
            if isinstance(creation, list):
                creation = creation[0]
            if isinstance(expiry, list):
                expiry = expiry[0]

            creation = creation.strftime("%Y-%m-%d") if isinstance(creation, datetime.date) else "N/A"
            expiry = expiry.strftime("%Y-%m-%d") if isinstance(expiry, datetime.date) else "N/A"

        except Exception:
            registrar = creation = expiry = "N/A"

        async def fetch_dns_record(record_type):
            url = f"https://dns.google/resolve?name={domain}&type={record_type}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    return await response.json()

        dns_A = await fetch_dns_record("A")
        dns_MX = await fetch_dns_record("MX")
        dns_NS = await fetch_dns_record("NS")
        dns_TXT = await fetch_dns_record("TXT")

        def parse_dns(data):
            if "Answer" not in data:
                return "N/A"
            return "\n".join([a.get("data", "") for a in data["Answer"]])

        # Reverse DNS
        try:
            reverse_dns = socket.gethostbyaddr(ip_address)[0]
        except:
            reverse_dns = "N/A"

        # SSL Certificate info
        try:
            ctx_ssl = ssl.create_default_context()
            with ctx_ssl.wrap_socket(socket.socket(), server_hostname=domain) as s:
                s.settimeout(3)
                s.connect((domain, 443))
                cert = s.getpeercert()

            ssl_issuer = cert.get("issuer", [["N/A"]])[0][0][1]
            ssl_valid_from = cert.get("notBefore", "N/A")
            ssl_valid_to = cert.get("notAfter", "N/A")

        except:
            ssl_issuer = ssl_valid_from = ssl_valid_to = "N/A"

        # Embed finale
        embed = discord.Embed(
            title=f"🌐 Domain Lookup: {domain}",
            color=discord.Color.green()
        )

        embed.add_field(name="🔢 IP", value=ip_address, inline=True)
        embed.add_field(name="🌍 Paese", value=ip_data.get("country", "N/A"), inline=True)
        embed.add_field(name="📍 Città", value=ip_data.get("city", "N/A"), inline=True)
        embed.add_field(name="🌐 ISP / Hosting", value=ip_data.get("isp", "N/A"), inline=True)
        embed.add_field(name="🏢 ASN", value=ip_data.get("as", "N/A"), inline=True)
        embed.add_field(name="🔁 Reverse DNS", value=reverse_dns, inline=False)

        embed.add_field(name="📡 DNS A", value=parse_dns(dns_A), inline=False)
        embed.add_field(name="📬 DNS MX", value=parse_dns(dns_MX), inline=False)
        embed.add_field(name="🧭 DNS NS", value=parse_dns(dns_NS), inline=False)
        embed.add_field(name="📝 DNS TXT", value=parse_dns(dns_TXT), inline=False)

        embed.add_field(name="🏛️ Registrar", value=registrar, inline=True)
        embed.add_field(name="📅 Creato il", value=creation, inline=True)
        embed.add_field(name="⏳ Scadenza", value=expiry, inline=True)

        embed.add_field(name="🔐 SSL Issuer", value=ssl_issuer, inline=False)
        embed.add_field(name="📆 SSL Valido da", value=ssl_valid_from, inline=True)
        embed.add_field(name="📆 SSL Valido fino a", value=ssl_valid_to, inline=True)

        embed.set_footer(text="Powered by ip-api.com + Google DNS + WHOIS + SSL")

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(DomainLookup(bot))