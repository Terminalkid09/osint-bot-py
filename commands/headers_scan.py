import aiohttp
import discord
from discord.ext import commands

class HeaderScan(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def headers(self, ctx, url: str):
        """Mostra header HTTP, redirect chain e sicurezza"""

        # Aggiunge https:// se manca
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url

        await ctx.send(f"🔍 Scansione header per: {url}")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, allow_redirects=True) as response:
                    headers = response.headers
                    status = response.status
                    final_url = str(response.url)
                    history = response.history 
                    cookies = response.cookies
        except Exception as e:
            await ctx.send(f"❌ Errore durante la richiesta: `{e}`")
            return

        embed = discord.Embed(
            title="🧩 HTTP Header Scan — Risultati",
            description=f"**URL finale:** `{final_url}`\n**Status:** `{status}`",
            color=discord.Color.blue()
        )

        # Redirect chain
        if history:
            chain = "\n".join([f"{h.status} → {h.url}" for h in history])
            embed.add_field(name="🔀 Redirect Chain", value=chain, inline=False)
        else:
            embed.add_field(name="🔀 Redirect Chain", value="Nessun redirect", inline=False)

        # Header principali
        important_headers = [
            "Server", "X-Powered-By", "Content-Type", "Content-Encoding",
            "Strict-Transport-Security", "Content-Security-Policy",
            "X-Frame-Options", "X-XSS-Protection", "X-Content-Type-Options",
            "Referrer-Policy"
        ]

        header_text = ""
        for h in important_headers:
            header_text += f"**{h}:** `{headers.get(h, 'N/A')}`\n"

        embed.add_field(name="📌 Header Principali", value=header_text, inline=False)

        # Sicurezza HTTP
        security_checks = {
            "Strict-Transport-Security": "HSTS attivo",
            "Content-Security-Policy": "CSP attiva",
            "X-Frame-Options": "Protezione clickjacking",
            "X-XSS-Protection": "Protezione XSS",
            "X-Content-Type-Options": "Protezione MIME sniffing",
            "Referrer-Policy": "Policy referrer impostata"
        }

        security_text = ""
        for header, meaning in security_checks.items():
            if header in headers:
                security_text += f"🟢 **{meaning}** (`{header}` presente)\n"
            else:
                security_text += f"🔴 **{meaning}** (`{header}` mancante)\n"

        embed.add_field(name="🔐 Sicurezza HTTP", value=security_text, inline=False)

        # Cookie e flag di sicurezza
        if cookies:
            cookie_text = ""
            for name, cookie in cookies.items():
                cookie_text += (
                    f"🍪 **{name}**\n"
                    f"- Secure: `{cookie['secure']}`\n"
                    f"- HttpOnly: `{cookie['httponly']}`\n"
                    f"- SameSite: `{cookie.get('samesite', 'N/A')}`\n\n"
                )
            embed.add_field(name="🍪 Cookie", value=cookie_text, inline=False)
        else:
            embed.add_field(name="🍪 Cookie", value="Nessun cookie rilevato", inline=False)

        # Header completi anche se un po' liminati
        count = 0
        full_headers = ""
        for key, value in headers.items():
            if count >= 15:
                full_headers += "\n… (altri header nascosti)"
                break
            full_headers += f"**{key}:** `{value}`\n"
            count += 1

        embed.add_field(name="📄 Header Completi (limitati)", value=full_headers, inline=False)

        embed.set_footer(text="HTTP Header Scanner PRO")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(HeaderScan(bot))