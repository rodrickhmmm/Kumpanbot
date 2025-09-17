import discord
from discord.ext import commands

TOKEN = "" # Replace with your bot's token

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.voice_states = True
intents.reactions = True

COG_MODULES = [
    "play", "skip", "stop", "pause", "resume",
    "queue", "nowplaying", "volume", "join", "leave",
    "loop", "ping",
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
    
@bot.command(name="help")
async def help_cmd(ctx: commands.Context):
    embed = discord.Embed(title="Kumpánovské příkazy", color=discord.Color.purple())
    embed.add_field(name="můžeš buďto použít / a nebo k! k zadávání příkazů", value=" ", inline=False)
    embed.add_field(name="/hraj <název|link>", value="Najde top 5 skladeb nebo přehraje hudbu z YouTube odkazu", inline=False)
    embed.add_field(name="/preskocit", value="Přeskoč aktuální hudbu", inline=True)
    embed.add_field(name="/prestat", value="Zastav aktuální hudbu a vymaže frontu", inline=True)
    embed.add_field(name="/pauzni", value="Pozastavit nebo Pokračovat v hraní hudby", inline=False)
    embed.add_field(name="/smycka", value="Zapne/vypne loopování hudby", inline=False)
    embed.add_field(name="/fronta", value="Zobrazí frontu", inline=True)
    embed.add_field(name="/nynihraje", value="Právě hraje", inline=True)
    embed.add_field(name="/hlasitost <0-200>", value="Hlasitost", inline=True)
    embed.add_field(name="/pripoj / /odpoj", value="Přivolej bota do voicu / Leavne voice", inline=True)
    embed.add_field(name="/ping", value="Zkontroluj aktuální odezvu bota v milisekundách", inline=False)
    await ctx.reply(embed=embed)



# Slash command version of help
@bot.tree.command(name="help", description="Show bot commands")
async def help_slash(interaction: discord.Interaction):
    embed = discord.Embed(title="Kumpánovské příkazy", color=discord.Color.purple())
    embed.add_field(name="můžeš buďto použít / a nebo k! k zadávání příkazů", value=" ", inline=False)
    embed.add_field(name="/hraj <název|link>", value="Najde top 5 skladeb nebo přehraje hudbu z YouTube odkazu", inline=False)
    embed.add_field(name="/preskocit", value="Přeskoč aktuální hudbu", inline=True)
    embed.add_field(name="/prestat", value="Zastav aktuální hudbu a vymaže frontu", inline=True)
    embed.add_field(name="/pauzni", value="Pozastavit nebo Pokračovat v hraní hudby", inline=False)
    embed.add_field(name="/smycka", value="Zapne/vypne loopování hudby", inline=False)
    embed.add_field(name="/fronta", value="Zobrazí frontu", inline=True)
    embed.add_field(name="/nynihraje", value="Právě hraje", inline=True)
    embed.add_field(name="/hlasitost <0-200>", value="Hlasitost", inline=True)
    embed.add_field(name="/pripoj / /odpoj", value="Přivolej bota do voicu / Leavne voice", inline=True)
    embed.add_field(name="/ping", value="Zkontroluj aktuální odezvu bota v milisekundách", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)


if __name__ == "__main__":
    if TOKEN.count(".") != 2 or any(c.isspace() for c in TOKEN):
        raise RuntimeError("The token has an invalid format. Please check it again in the Developer Portal.")
    bot.run(TOKEN)
