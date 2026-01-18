import discord
from discord.ext import commands
import dns.resolver

class DNSLookup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def dns(self, ctx, domain: str):
        """DNS Lookup PRO per un dominio"""

        embed = discord.Embed(
            title=f"🌐 DNS Lookup — {domain}",
            color=discord.Color.blue()
        )

        record_types = ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA"]

        for rtype in record_types:
            try:
                answers = dns.resolver.resolve(domain, rtype)
                result = "\n".join([str(r) for r in answers])
            except Exception:
                result = "N/A"

            embed.add_field(name=f"🔹 {rtype}", value=f"`{result}`", inline=False)

        # SPF e DMARC (TXT parsing)
        try:
            txt_records = dns.resolver.resolve(domain, "TXT")
            spf = [str(r) for r in txt_records if "v=spf1" in str(r)]
            dmarc = [str(r) for r in txt_records if "v=DMARC1" in str(r)]
        except:
            spf = []
            dmarc = []

        embed.add_field(name="🛡️ SPF", value="`" + (spf[0] if spf else "N/A") + "`", inline=False)
        embed.add_field(name="🛡️ DMARC", value="`" + (dmarc[0] if dmarc else "N/A") + "`", inline=False)

        embed.set_footer(text="DNS Lookup PRO")

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(DNSLookup(bot))