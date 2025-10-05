import discord
from discord.ext import commands
from bot_token import TOKEN

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.voice_states = True
intents.reactions = True

COG_MODULES = [
    "play", "skip", "stop", "pause", "resume",
    "queue", "nowplaying", "volume", "join", "leave",
    "loop", "ping", "citaty",
]

class KumpanBot(commands.Bot):
    async def setup_hook(self):
        for name in COG_MODULES:
            await self.load_extension(f"cogs.{name}")
        # Sync slash commands instantly to your test guild
        await self.tree.sync()

bot = KumpanBot(
    command_prefix=commands.when_mentioned_or("k!", "K!"),
    intents=intents,
    help_command=None,
    case_insensitive=True,   
)

@bot.event
async def on_ready():
    print(f"Přihlášen jako {bot.user} (IDéčko: {bot.user.id})")
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.listening, name="Vráťa Hošek")
    )
    await bot.tree.sync()  # Ensure slash commands are synced

@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, commands.CheckFailure):
        return
    original = getattr(error, "original", error)
    msg = str(original) or "An error occurred while executing the command."
    try:
        await ctx.reply(msg)
    except Exception:
        await ctx.send(msg)
    
@bot.command(name="prikazy")
async def help_cmd(ctx: commands.Context):
    embed = discord.Embed(title="Kumpánovské příkazy", color=discord.Color.purple())
    embed.set_thumbnail(url="https://images.uncyclomedia.co/necyklopedie/cs/thumb/f/f8/Frantisekreditel.jpg/250px-Frantisekreditel.jpg")
    embed.add_field(name="můžeš buďto použít / a nebo k! k zadávání příkazů", value=" ", inline=False)
    embed.add_field(name="/hraj <název|link>", value="Najde top 5 skladeb nebo přehraje hudbu z YouTube odkazu", inline=False)
    embed.add_field(name="/preskocit", value="Přeskoč aktuální hudbu", inline=False)
    embed.add_field(name="/prestat", value="Zastav aktuální hudbu a vymaže frontu", inline=False)
    embed.add_field(name="/pauzni", value="Pozastavit nebo Pokračovat v hraní hudby", inline=False)
    embed.add_field(name="/smycka", value="Zapne/vypne loopování hudby", inline=False)
    embed.add_field(name="/fronta", value="Zobrazí frontu", inline=False)
    embed.add_field(name="/nynihraje", value="Právě hraje", inline=False)
    embed.add_field(name="/hlasitost <0-200>", value="Hlasitost", inline=False)
    embed.add_field(name="/pripoj / /odpoj", value="Přivolej bota do voicu / Leavne voice", inline=False)
    embed.add_field(name="/ping", value="Zkontroluj aktuální odezvu bota v milisekundách", inline=False)
    embed.add_field(name="─────────────────────────────────────────────", value=" ", inline= False)
    embed.add_field(name="Maty Mythic má oficiální zákaz používat tohoto bota", value=" ", inline=False)
    embed.add_field(name="Platí také oficiální zákaz na mongolskej heavy metal, indickej phonk, čínskej rap a českej rap", value=" ", inline=False)
    embed.add_field(name="Jestli si nemyslíš že Vráťa Hošek je nejlepší, tak toho bota rovnou smaž", value=" ", inline=False)
    await ctx.reply(embed=embed)

@bot.tree.command(name="prikazy", description="Ukáže přikázy které řinčák používá")
async def help_slash(interaction: discord.Interaction):
    embed = discord.Embed(title="Kumpánovské příkazy", color=discord.Color.purple())
    embed.set_thumbnail(url="https://images.uncyclomedia.co/necyklopedie/cs/thumb/f/f8/Frantisekreditel.jpg/250px-Frantisekreditel.jpg")
    embed.add_field(name="můžeš buďto použít / a nebo k! k zadávání příkazů", value=" ", inline=False)
    embed.add_field(name="/hraj <název|link>", value="Najde top 5 skladeb nebo přehraje hudbu z YouTube odkazu", inline=False)
    embed.add_field(name="/preskocit", value="Přeskoč aktuální hudbu", inline=False)
    embed.add_field(name="/prestat", value="Zastav aktuální hudbu a vymaže frontu", inline=False)
    embed.add_field(name="/pauzni", value="Pozastavit nebo Pokračovat v hraní hudby", inline=False)
    embed.add_field(name="/smycka", value="Zapne/vypne loopování hudby", inline=False)
    embed.add_field(name="/fronta", value="Zobrazí frontu", inline=False)
    embed.add_field(name="/nynihraje", value="Právě hraje", inline=False)
    embed.add_field(name="/hlasitost <0-200>", value="Hlasitost", inline=False)
    embed.add_field(name="/pripoj / /odpoj", value="Přivolej bota do voicu / Leavne voice", inline=False)
    embed.add_field(name="/ping", value="Zkontroluj aktuální odezvu bota v milisekundách", inline=False)
    embed.add_field(name="─────────────────────────────────────────────", value=" ", inline= False)
    embed.add_field(name="Maty Mythic má oficiální zákaz používat tohoto bota", value=" ", inline=False)
    embed.add_field(name="Platí také oficiální zákaz na mongolskej heavy metal, indickej phonk, čínskej rap a českej rap", value=" ", inline=False)
    embed.add_field(name="Jestli si nemyslíš že Vráťa Hošek je nejlepší, tak toho bota rovnou smaž", value=" ", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

    
@bot.tree.command(name="orincakovy", description="Řekne ti informace o botovy")
async def about_slash(interaction: discord.Interaction):
    embed = discord.Embed(title="O řinčákovy", color=discord.Color.purple())
    embed.set_thumbnail(url="https://images.uncyclomedia.co/necyklopedie/cs/thumb/f/f8/Frantisekreditel.jpg/250px-Frantisekreditel.jpg")
    embed.add_field(name="Github link: https://github.com/rodrickhmmm/Kumpanbot", value=" ", inline=False)
    embed.add_field(name="Jsem řinčák co je jen dostupný na Mým Kumpánům",value="",inline=False)
    embed.add_field(name="Přehrávám hudbu a sloužím i na ostatní věci",value="",inline=False)
    embed.add_field(name="Jsem forknutý z řinčáka Oguri, link: https://github.com/withoutminh/Oguri",value="",inline=False)
    embed.add_field(name="Naprogramoval mě: původní kód - withoutminh, upravený a přidaný věci - Rodrick_ (rodrickhmmm) a Ocasník (xtomasnemec)", value="", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)


if __name__ == "__main__":
    if TOKEN.count(".") != 2 or any(c.isspace() for c in TOKEN):
        raise RuntimeError("The token has an invalid format. Please check it again in the Developer Portal.")
    bot.run(TOKEN)
