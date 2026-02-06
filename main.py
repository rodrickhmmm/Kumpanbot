import discord
from discord.ext import commands
from bot_token import TOKEN
import random

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.voice_states = True
intents.reactions = True
intents.members = True

COG_MODULES = [
    # Hudební příkazy (0-12)
    "hraj", "preskocit", "prestat", "pauzni", "pokracuj",
    "fronta", "nynihraje", "hlasitost", "pripoj", "odpoj",
    "smycka", "vycistitfrontu", "vratahosek",
    # Běžné funkce (13-18)
    "ping", "citat", "narozeniny", "obejmout", "grok", "grokAImode",
    # Admin příkazy (19-25)
    "gulag", "antigulag", "obnovitymaty", "reakcnirole",
    "banmatymythic", "unbanmatymythic", "nacistprikazy",
    "horsi_nez_modrej",
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
    print('-----')

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
    embed.add_field(name="/hraj <název|link>", value="Najde top 5 skladeb nebo přehraje hudbu z YouTube/SoundCloud odkazu", inline=False)
    embed.add_field(name="/preskocit", value="Přeskoč aktuální hudbu", inline=False)
    embed.add_field(name="/prestat", value="Zastav aktuální hudbu a vymaže frontu", inline=False)
    embed.add_field(name="/pauzni", value="Pozastavit nebo Pokračovat v hraní hudby", inline=False)
    embed.add_field(name="/smycka", value="Zapne/vypne loopování hudby", inline=False)
    embed.add_field(name="/fronta", value="Zobrazí frontu", inline=False)
    embed.add_field(name="/nynihraje", value="Právě hraje", inline=False)
    embed.add_field(name="/hlasitost <0-200>", value="Hlasitost", inline=False)
    embed.add_field(name="/pripoj / /odpoj", value="Přivolej bota do voicu / Leavne voice", inline=False)
    embed.add_field(name="/ping", value="Zkontroluj aktuální odezvu bota v milisekundách", inline=False)
    embed.add_field(name="/grok", value="Je toto pravda?", inline=False)
    embed.add_field(name="/grokaimode", value="Grok ti vygeneruje ten nejvíc židovskej text automaticky (command: pravda/nepravda)", inline=False)
    embed.add_field(name="─────────────────────────────────────────────", value=" ", inline= False)
    embed.add_field(name="Maty Mythic má oficiální zákaz používat tohoto bota", value=" ", inline=False)
    embed.add_field(name="Platí také oficiální zákaz na mongolskej heavy metal, indickej phonk, čínskej rap a českej rap", value=" ", inline=False)
    embed.add_field(name="Jestli si nemyslíš že Vráťa Hošek je nejlepší, tak toho bota rovnou smaž", value=" ", inline=False)
    await ctx.reply(embed=embed)

description_commands = [
    "Přehraje skladbu podle názvu nebo odkazu z YouTubu nebo SoundCloudu",  # /hraj
    "Přeskočí přehrávanou skladbu",  # /preskocit
    "Zastaví hudbu a opustí chcall",  # /prestat
    "Pauzne přehrávanou hudbu",  # /pauzni
    "Pokračuje v přehrávání hudby",  # /pokracuj
    "Zobrazí frontu skladeb",  # /fronta
    "Zobrazí momentálně přehrávanou skladbu",  # /nynihraje
    "Nastaví hlasitost bota (mezi 0 až 200)",  # /hlasitost
    "Řinčák se připojí do chcallu",  # /pripoj
    "Řinčák se odpojí ze chcallu",  # /odpoj
    "Zapne/vypne opakování přehrávané skladby",  # /smycka
    "Vyčistí frontu skladeb",  # /vycistitfrontu
    "Přehraje ten nejvíce peak playlist od toho nejvíc peak umělce",  # /vratahosek
    "Zkontroluje řinčákovu rychlost",  # /ping
    "Vytvoř citát pokud někdo řekl např. nějakou volovinu",  # /citat
    "Popřej někomu hodně štěstí zdraví k dnu tvého narození",  # /narozeniny
    "Obejmi někoho",  # /obejmout
    "Naše verze známého \"@Grok, je toto pravda?\"",  # /grok
    "Stejný jako /grok, ale tento ti vygeneruje automaticky text na základě jestli je zpráva na kterou se ptáš pravda nebo nepravda",  # /grokaimode
    "Horší než modrej meme generátor",  # /horsi_nez_modrej
]


# Admin příkazy (indexy 19-25)
admin_commands = [
    "Proště ho pošleš do gulagu, protože nikam jinam se takoví lidé nehodí",  # /gulag
    "Vrátí ho z gulagu",  # /antigulag
    "Přidáš uživateli role který měl Maty",  # /obnovitymaty
    "Nastaví reakční roli",  # /reakcnirole
    "Zabanuje Matyho (Elitní reference :ticovedi:)",  # /banmatymythic
    "Odbanuje Matyho",  # /unbanmatymythic
    "Znova přenačtě příkazy"  # /nacistprikazy
]

# Dekorátor pro admin-only slash příkazy
from discord import app_commands

@bot.tree.command(name="prikazy", description="Ukáže přikázy které řinčák používá")
async def help_slash(interaction: discord.Interaction):
    # První embed - hudební příkazy (0-12)
    embed1 = discord.Embed(title="🎵 Kumpánovské příkazy - Hudba", color=discord.Color.purple())
    embed1.set_thumbnail(url="https://images.uncyclomedia.co/necyklopedie/cs/thumb/f/f8/Frantisekreditel.jpg/250px-Frantisekreditel.jpg")
    for i in range(13):
        embed1.add_field(name="/"+COG_MODULES[i], value=description_commands[i], inline=False)
    embed1.add_field(name="─────────────────────────────────────────────", value=" ", inline= False)
    embed1.add_field(name="Platí také oficiální zákaz na mongolskej heavy metal, indickej phonk, čínskej rap a českej rap", value=" ", inline=False)
    
    # Druhý embed - běžné funkce (13-18)
    embed2 = discord.Embed(title="⚙️ Kumpánovské příkazy - Další příkazy", color=0x835ee8)
    embed2.set_thumbnail(url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSbS-MoygD4RCPEZpH3X7zhSf4QPOrgH25WWA&s")
    for i in range(13, 19):
        embed2.add_field(name="/"+COG_MODULES[i], value=description_commands[i], inline=False)
    embed2.add_field(name="─────────────────────────────────────────────", value=" ", inline= False)
    embed2.add_field(name="Maty Mythic má oficiální zákaz používat tohoto bota", value=" ", inline=False)
    embed2.add_field(name="Jestli si nemyslíš že Vráťa Hošek je nejlepší, tak toho bota rovnou smaž", value=" ", inline=False)
    
    # Třetí embed - admin příkazy (19-25) pouze pro adminy
    embeds = [embed1, embed2]
    if interaction.user.guild_permissions.administrator:
        embed3 = discord.Embed(title="🔒 Admin příkazy", color=discord.Color.red())
        embed3.set_thumbnail(url="https://images.uncyclomedia.co/necyklopedie/cs/d/db/Franti%C5%A1k%C5%AFv_%C5%99editelsk%C3%BD_sal%C3%A1t.jpg")
        for i in range(19, 26):
            embed3.add_field(name="/"+COG_MODULES[i], value=admin_commands[i-19], inline=False)
        embed3.add_field(name="─────────────────────────────────────────────", value=" ", inline= False)
        embed3.add_field(name="Tyto příkazy můžou používat jenom agenti KGB a GRU, nikdo jiný!!!", value=" ", inline=False)
        embeds.append(embed3)
    await interaction.response.send_message(embeds=embeds, ephemeral=True)

    
@bot.tree.command(name="orincakovy", description="Řekne ti informace o botovi")
async def about_slash(interaction: discord.Interaction):
    embed = discord.Embed(title="O řinčákovy", color=discord.Color.purple())
    embed.set_thumbnail(url="https://images.uncyclomedia.co/necyklopedie/cs/thumb/f/f8/Frantisekreditel.jpg/250px-Frantisekreditel.jpg")
    embed.add_field(name="Github link: https://github.com/rodrickhmmm/Kumpanbot", value=" ", inline=False)
    embed.add_field(name="Jsem řinčák co je jen dostupný na Mým Kumpánům",value="",inline=False)
    embed.add_field(name="Přehrávám hudbu a sloužím i na ostatní věci",value="",inline=False)
    embed.add_field(name="Jsem forknutý z řinčáka Oguri, link: https://github.com/withoutminh/Oguri",value="",inline=False)
    embed.add_field(name="Naprogramoval mě: původní kód - withoutminh, upravený a přidaný věci - Rodrick_ (rodrickhmmm) a Ocasník (xtomasnemec)", value="", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

# Welcome channel ID - right-click channel and Copy ID (Developer mode must be on)
WELCOME_CHANNEL_ID = 1366162083733049534

maty = 1150085087451435102

@bot.event
async def on_member_join(member):
    pozdravy = [
        "Čůs negře! {member.name}",
        "Připojila se nějaká koninka s názvem {member.name}",
        "Co je to tu za mldku {member.name} ?",
        "Novej kumpán {member.name} (snad lepší jak Maty 🤞)"
    ]

    if member.id == maty:
        print(f"/unbanmatymythic")
        cusnegre = f"/unbanmatymythic"
    else:
        poradi = random.randint(0,(len(pozdravy)-1))
        print(pozdravy[poradi])
        cusnegre = pozdravy[poradi].format(member=member)
    
    # Try to send DM to the new member
    try:
        await member.send(f"MLDKO {member.name}, právě ses objevil na tom nejvíc tuff serveru.")
        print(f"Poslal jsem zprávu konynce {member.name}")
    except:
        print(f"Nepodařilo se poslat zprávu konynce {member.name}")
    
    # Send welcome message in the welcome channel
    try:
        channel = bot.get_channel(WELCOME_CHANNEL_ID)
        if channel:
            embed = discord.Embed(
                title=f"Novej kumpán",
                description=f"{cusnegre}",
                color=discord.Color.purple()
            )
            await channel.send(embed=embed)
    except Exception as e:
        print(f"Chyba při posílání welcome zprávy: {e}")

@bot.event
async def on_member_remove(member):
    odzdravy = [
        "Koninka {member.name} odešla",
        "{member.name} tahle mldka to leavla",
        "Cigan {member.name} se vysral na kumpány"
    ]

    poradi = random.randint(0,(len(odzdravy)-1))
    if member.id == maty:
        print(f"/banmatymythic")
        papa = f"/banmatymythic"
    else:
        print(odzdravy[poradi].format(member=member))
        print(f"Koninka {member.name} odešla")
        papa = odzdravy[poradi].format(member=member)
    
    # Send goodbye message in the welcome channel
    try:
        channel = bot.get_channel(WELCOME_CHANNEL_ID)
        if channel:
            embed = discord.Embed(
                title=f"-1 kumpán 😔",
                description=f"{papa}",
                color=discord.Color.red()
            )
            await channel.send(embed=embed)
    except Exception as e:
        print(f"Chyba při posílání goodbye zprávy: {e}")

if __name__ == "__main__":
    if TOKEN.count(".") != 2 or any(c.isspace() for c in TOKEN):
        raise RuntimeError("The token has an invalid format. Please check it again in the Developer Portal.")
    bot.run(TOKEN)
