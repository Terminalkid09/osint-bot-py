import discord
from discord.ext import commands
import re
import dns.resolver
import aiohttp

class EmailOSINT(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def email(self, ctx, email: str):
        """OSINT avanzato su un indirizzo email"""

        # Validazione formale email
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(pattern, email):
            await ctx.send("❌ Email non valida. Esempio corretto: `nome@example.com`")
            return

        # Estrazione dominio
        domain = email.split("@")[1]

        embed = discord.Embed(
            title="📧 Email OSINT — Risultati",
            description=f"Analisi per: `{email}`",
            color=discord.Color.blue()
        )

        embed.add_field(name="🔹 Dominio", value=f"`{domain}`", inline=False)

        # MX Lookup
        try:
            mx_records = dns.resolver.resolve(domain, "MX")
            mx_list = [str(r.exchange) for r in mx_records]
            embed.add_field(name="📮 MX Records", value="\n".join(f"`{m}`" for m in mx_list), inline=False)
        except:
            embed.add_field(name="📮 MX Records", value="N/A", inline=False)

        # SPF / DMARC (TXT parsing)
        try:
            txt_records = dns.resolver.resolve(domain, "TXT")
            txt_list = [str(r) for r in txt_records]

            spf = next((t for t in txt_list if "v=spf1" in t), "N/A")
            dmarc = next((t for t in txt_list if "v=DMARC1" in t), "N/A")

        except:
            spf = "N/A"
            dmarc = "N/A"

        embed.add_field(name="🛡️ SPF", value=f"`{spf}`", inline=False)
        embed.add_field(name="🛡️ DMARC", value=f"`{dmarc}`", inline=False)

        # Breach Check (API pubblica)
        breach_info = "N/A"
        try:
            url = f"https://api.proxynova.com/comb?email={email}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    data = await response.json()
                    if data.get("found"):
                        breach_info = f"⚠️ Trovate {data['count']} occorrenze in leak pubblici"
                    else:
                        breach_info = "🟢 Nessun leak trovato"
        except:
            breach_info = "N/A"

        embed.add_field(name="🔓 Breach Check", value=breach_info, inline=False)

        # Tipo di dominio
        free_domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com", "proton.me"]

        if domain in free_domains:
            domain_type = "📨 Email gratuita"
        else:
            domain_type = "🏢 Dominio personalizzato / aziendale"

        embed.add_field(name="🏷️ Tipo dominio", value=domain_type, inline=False)

        embed.set_footer(text="Email OSINT PRO")

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(EmailOSINT(bot))