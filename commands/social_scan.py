import aiohttp
import discord
from discord.ext import commands

class SocialScan(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def social(self, ctx, username: str):
        """Scansione OSINT avanzata per username"""

        await ctx.send(f"🔍 Scansione social avanzata per: `{username}`")

        # Piattaforme da controllare
        platforms = {
            "Instagram": f"https://www.instagram.com/{username}/",
            "Twitter": f"https://x.com/{username}",
            "TikTok": f"https://www.tiktok.com/@{username}",
            "GitHub": f"https://github.com/{username}",
            "Reddit": f"https://www.reddit.com/user/{username}",
            "Steam": f"https://steamcommunity.com/id/{username}",
            "Pinterest": f"https://www.pinterest.com/{username}/",
            "Twitch": f"https://www.twitch.tv/{username}",
            "YouTube": f"https://www.youtube.com/@{username}",
        }

        results = {}

        async with aiohttp.ClientSession() as session:

            # Controllo presenza profili
            for name, url in platforms.items():
                try:
                    async with session.get(url, allow_redirects=True) as response:
                        if response.status == 200:
                            results[name] = url
                        else:
                            results[name] = None
                except:
                    results[name] = None

            # GitHub
            github_data = None
            try:
                async with session.get(f"https://api.github.com/users/{username}") as r:
                    if r.status == 200:
                        github_data = await r.json()
            except:
                pass

            # Reddit
            reddit_data = None
            try:
                async with session.get(f"https://www.reddit.com/user/{username}/about.json",
                                       headers={"User-Agent": "Mozilla/5.0"}) as r:
                    if r.status == 200:
                        reddit_data = await r.json()
            except:
                pass

            # 4) BreachDirectory => ricerca username
            breach_data = None
            try:
                async with session.get(f"https://breachdirectory.org/api/search?query={username}") as r:
                    breach_data = await r.json()
            except:
                pass

        # EMBED RISULTATI
        embed = discord.Embed(
            title=f"🌐 Social Scan — {username}",
            color=discord.Color.blue()
        )

        # Risultati piattaforme
        for platform, link in results.items():
            if link:
                embed.add_field(
                    name=f"🟢 {platform}",
                    value=f"[Profilo trovato]({link})",
                    inline=False
                )
            else:
                embed.add_field(
                    name=f"🔴 {platform}",
                    value="Non trovato",
                    inline=False
                )

        # GitHub
        if github_data:
            embed.add_field(
                name="🐙 GitHub Info",
                value=(
                    f"**Repo pubblici:** {github_data.get('public_repos', 'N/A')}\n"
                    f"**Followers:** {github_data.get('followers', 'N/A')}\n"
                    f"**Account creato:** {github_data.get('created_at', 'N/A')}"
                ),
                inline=False
            )

        # Reddit
        if reddit_data:
            user = reddit_data.get("data", {})
            embed.add_field(
                name="👽 Reddit Info",
                value=(
                    f"**Karma:** {user.get('total_karma', 'N/A')}\n"
                    f"**Account creato:** {user.get('created_utc', 'N/A')}"
                ),
                inline=False
            )

        # BreachDirectory
        if breach_data and breach_data.get("result"):
            leaks = breach_data["result"][:5]
            leak_text = "\n".join([f"🔓 {entry.get('source', 'Sconosciuto')}" for entry in leaks])

            embed.add_field(
                name="⚠️ Username trovato in Data Breach",
                value=leak_text,
                inline=False
            )
        else:
            embed.add_field(
                name="🟢 Nessun Data Breach trovato",
                value="L'username non compare in database compromessi.",
                inline=False
            )

        embed.set_footer(text="OSINT Social Scanner PRO")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(SocialScan(bot))