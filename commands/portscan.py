import asyncio
import socket
import discord
from discord.ext import commands

class PortScanner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Mappa OSINT porta => servizio
        self.service_map = {
            21: "FTP",
            22: "SSH",
            23: "Telnet",
            25: "SMTP",
            53: "DNS",
            80: "HTTP",
            110: "POP3",
            143: "IMAP",
            443: "HTTPS",
            3306: "MySQL",
            3389: "RDP",
            8080: "HTTP-Proxy",
            8443: "HTTPS-Alt"
        }

    async def scan_port(self, host, port):
        """Scansiona una porta, identifica il servizio e prova a leggere il banner"""
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port),
                timeout=1.5
            )

            try:
                banner = await asyncio.wait_for(reader.read(256), timeout=1)
                banner = banner.decode(errors="ignore").strip()
                if not banner:
                    banner = "Nessun banner"
            except:
                banner = "Nessun banner"

            writer.close()
            await writer.wait_closed()

            # Identificazione servizio
            service = self.service_map.get(port, "Sconosciuto")

            return port, service, banner

        except:
            return None

    @commands.command()
    async def portscan(self, ctx, host: str, ports: str = None):
        """
        Scansiona porte comuni o un range personalizzato.
        Esempi:
        !portscan google.com
        !portscan 1.1.1.1 1-1000
        """

        await ctx.send(f"🔍 Scansione porte per: `{host}`")

        # Controllo host raggiungibile
        try:
            socket.gethostbyname(host)
        except:
            await ctx.send("❌ Host non valido o non raggiungibile.")
            return

        # Porte comuni se non specificato
        common_ports = [
            21, 22, 23, 25, 53, 80, 110, 143,
            443, 3306, 3389, 8080, 8443
        ]

        if ports:
            try:
                start, end = ports.split("-")
                start = int(start)
                end = int(end)

                if start < 1 or end > 65535 or start >= end:
                    await ctx.send("❌ Range porte non valido.")
                    return

                port_list = list(range(start, end + 1))

            except:
                await ctx.send("❌ Usa il formato corretto: `1-1000`")
                return
        else:
            port_list = common_ports

        # Scansione asincrona
        tasks = [self.scan_port(host, port) for port in port_list]
        results = await asyncio.gather(*tasks)

        open_ports = [r for r in results if r]

        embed = discord.Embed(
            title=f"🧪 Port Scan — {host}",
            color=discord.Color.blue()
        )

        if open_ports:
            for port, service, banner in open_ports[:25]:  # Limite per non spammare
                embed.add_field(
                    name=f"🟢 Porta {port} aperta ({service})",
                    value=f"**Banner:** `{banner}`",
                    inline=False
                )
        else:
            embed.add_field(
                name="🔴 Nessuna porta aperta trovata",
                value="Il server non espone servizi rilevabili.",
                inline=False
            )

        embed.set_footer(text="OSINT Port Scanner PRO")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(PortScanner(bot))