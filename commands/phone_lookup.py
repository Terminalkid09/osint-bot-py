import discord
from discord.ext import commands
import phonenumbers
from phonenumbers import geocoder, carrier, number_type, PhoneNumberType

class PhoneLookup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def phone(self, ctx, number: str):
        """OSINT avanzato su un numero di telefono"""

        # Parsing del numero
        try:
            parsed = phonenumbers.parse(number, None)
        except Exception:
            await ctx.send("❌ Numero non valido. Usa il formato internazionale, esempio: `+393401234567`")
            return

        # Validazione
        if not phonenumbers.is_valid_number(parsed):
            await ctx.send("❌ Numero non valido o inesistente.")
            return

        # Formati
        e164 = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        intl = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        national = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)

        # Paese (basato su prefisso, non sempre affidabile)
        country = geocoder.description_for_number(parsed, "it")
        country = country if country else "N/A (numero mobile o non geografico)"

        # Operatore (storico, non aggiornato)
        operator = carrier.name_for_number(parsed, "it")
        operator = operator if operator else "N/A (dato non disponibile o portabilità)"

        # Tipo di numero
        type_map = {
            PhoneNumberType.MOBILE: "📱 Mobile",
            PhoneNumberType.FIXED_LINE: "☎️ Fisso",
            PhoneNumberType.FIXED_LINE_OR_MOBILE: "📞 Fisso/Mobile",
            PhoneNumberType.VOIP: "🌐 VoIP",
            PhoneNumberType.TOLL_FREE: "🆓 Numero Verde",
            PhoneNumberType.PREMIUM_RATE: "💰 Premium",
            PhoneNumberType.SHARED_COST: "💸 Shared Cost",
            PhoneNumberType.UAN: "🏢 UAN",
            PhoneNumberType.UNKNOWN: "❓ Sconosciuto"
        }
        num_type = type_map.get(number_type(parsed), "❓ Sconosciuto")

        # Geograficità
        geographic = "Sì" if phonenumbers.is_number_geographical(parsed) else "No (mobile o virtuale)"

        # Embed Discord
        embed = discord.Embed(
            title="📞 Phone Number OSINT — Risultati",
            color=discord.Color.blue()
        )

        # Numero e formati
        embed.add_field(name="🔹 Numero inserito", value=f"`{number}`", inline=False)
        embed.add_field(name="🌐 Formato E.164", value=f"`{e164}`", inline=True)
        embed.add_field(name="🌍 Internazionale", value=f"`{intl}`", inline=True)
        embed.add_field(name="🏠 Nazionale", value=f"`{national}`", inline=True)

        # Info geografiche
        embed.add_field(name="🌍 Paese rilevato", value=country, inline=True)
        embed.add_field(name="📌 Geografico", value=geographic, inline=True)

        # Info operatore
        embed.add_field(name="🏢 Operatore storico", value=operator, inline=False)
        embed.add_field(name="📌 Tipo di numero", value=num_type, inline=True)

        # Validità
        embed.add_field(name="✔️ Valido", value="Sì", inline=True)
        embed.add_field(name="📏 Lunghezza input", value=str(len(number)), inline=True)

        embed.set_footer(text="Phone Number OSINT PRO — Dati indicativi, non garantiti")

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(PhoneLookup(bot))