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
        # Sync slash commands
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
    embed.add_field(name="o!play <name|link>", value="Find the top 5 songs or play music from a YouTube link", inline=False)
    embed.add_field(name="o!skip", value="Skip the current song", inline=True)
    embed.add_field(name="o!stop", value="Stop current song and clear the queue.", inline=True)
    embed.add_field(name="o!pause / o!resume", value="Pause / Resume", inline=False)
    embed.add_field(name="o!loop", value="Toggle repeat current track", inline=False)
    embed.add_field(name="o!queue", value="View the queue", inline=True)
    embed.add_field(name="o!np", value="Now playing", inline=True)
    embed.add_field(name="o!vol <0-200>", value="Volume", inline=True)
    embed.add_field(name="o!join / o!leave", value="Call the bot to join/leave the voice channel.", inline=True)
    embed.add_field(name="o!ping", value="Check the bot's current latency in milliseconds.", inline=False)
    await ctx.reply(embed=embed)


# Slash command version of help
@bot.tree.command(name="help", description="Show bot commands")
async def help_slash(interaction: discord.Interaction):
    embed = discord.Embed(title="Kumpánovské příkazy", color=discord.Color.purple())
    embed.add_field(name="o!play <name|link>", value="Find the top 5 songs or play music from a YouTube link", inline=False)
    embed.add_field(name="o!skip", value="Skip the current song", inline=True)
    embed.add_field(name="o!stop", value="Stop current song and clear the queue.", inline=True)
    embed.add_field(name="o!pause / o!resume", value="Pause / Resume", inline=False)
    embed.add_field(name="o!loop", value="Toggle repeat current track", inline=False)
    embed.add_field(name="o!queue", value="View the queue", inline=True)
    embed.add_field(name="o!np", value="Now playing", inline=True)
    embed.add_field(name="o!vol <0-200>", value="Volume", inline=True)
    embed.add_field(name="o!join / o!leave", value="Call the bot to join/leave the voice channel.", inline=True)
    embed.add_field(name="o!ping", value="Check the bot's current latency in milliseconds.", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

if __name__ == "__main__":
    if TOKEN.count(".") != 2 or any(c.isspace() for c in TOKEN):
        raise RuntimeError("The token has an invalid format. Please check it again in the Developer Portal.")
    bot.run(TOKEN)
