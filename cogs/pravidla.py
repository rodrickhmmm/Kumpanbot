import discord
from discord.ext import commands
from discord import app_commands

guild_id = 948315626131300402
test_guild = discord.Object(id=guild_id)

rules = [
    'Chovat se "slušně"',
    'Nepodporovat židobolševické zednáře',
    'Nword je zde povolen, ale nespamuj to jako bagoun (pokud netestuješ mikrofon nebo se ti nelaguje internet)',
    'Nebuď homofob a transfob, to fakt neni tuff bratře (Prostě se nechovej jak RP)',
    'Nebuď Maty (jakejkoliv), RP ani `D*n`',
    'Používat PhonkHub',
    'Nebýt kretén a bagoun (souvisí s 1. a 5. pravidlem)',
    'Poslouchat Tiki Tiki fonk',
    'NIKDY nepoužívat ani nezmiňovat Teema pozitivně',
    'Žádný porno (pouze v #🔞-dihh-cheese)',
    'Žádný GIMP uživatel',
    'Nepoužívat slovíčka na následujícím seznamu:',
    'b*no, B*no, br*o, Br*o, dan, Dan, david, David, demon hunters, deodorant, employed, employment, Hradec, Hradec Kralove, Hradec Králové, job, K pop, K-Pop Demon Hunters, Koupelna, kpop, parfém, práce, Praha, sampon, šampón, sprcha, Sprcha, Vamberk, ven, vonavka, voňavka, work, ZAV',
]

class Pravidla(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="pravidla", description="Zobrazí se pravidla.")
    async def pravidla(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Pravidla",
            description="",
            color=0xa518f2,
        )
        embed.set_thumbnail(url="https://i.pinimg.com/736x/ee/16/23/ee16238f87617c49892a8c9bcdf80a0f.jpg")
        for i in range(len(rules)):
            embed.description += f"{i+1}) {rules[i]}\n"
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Pravidla(bot))