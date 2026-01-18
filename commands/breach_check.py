import aiohttp
import discord
from discord.ext import commands
import re

class BreachCheck(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def breach(self, ctx, email: str):
        """Controlla se un'email è presente in data breach"""

        # Validazione email
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            await ctx.send("❌ L'email inserita non è valida.")
            return

        await ctx.send("🔍 Controllo in corso...")

        url = f"https://breachdirectory.org/api/search?query={email}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    data = await response.json()
        except Exception as e:
            await ctx.send(f"❌ Errore durante la richiesta: `{e}`")
            return

        # Nessun risultato
        if not data.get("success") or not data.get("result"):
            embed = discord.Embed(
                title="🟢 Nessun Data Breach trovato",
                description=f"L'email **{email}** non risulta in nessun leak conosciuto.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
            return

        # Risultati trovati
        embed = discord.Embed(
            title=f"🔴 Data Breach trovati per {email}",
            color=discord.Color.red()
        )

        leaks = data.get("result", [])[:10]

        for entry in leaks:
            source = entry.get("source", "Sconosciuto")
            password = entry.get("password", "Non disponibile")
            hash_type = entry.get("hash_type", "N/A")

            embed.add_field(
                name=f"🔓 Leak: {source}",
                value=f"**Password:** `{password}`\n**Hash:** `{hash_type}`",
                inline=False
            )

        embed.set_footer(text="Fonte: BreachDirectory.org (free API)")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(BreachCheck(bot))