# oguri.py
import discord
from discord.ext import commands

# ⚠️ Điền token thật của bạn vào đây (giữ nguyên dạng, KHÔNG thêm Bot, KHÔNG ngoặc)
TOKEN = "YOUR_TOKEN_HERE"

# Kiểm tra token hợp lệ (3 phần, có 2 dấu chấm)
if TOKEN.count(".") != 2 or any(c.isspace() for c in TOKEN):
    raise RuntimeError("Token có định dạng bất thường. Hãy kiểm tra lại trong Developer Portal.")

# Intents cho bot
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.voice_states = True
intents.reactions = True

# Danh sách các module lệnh trong thư mục cogs/
COG_MODULES = [
    "play", "skip", "stop", "pause", "resume",
    "queue", "nowplaying", "volume", "join", "leave",
]

# Bot class
class MusicBot(commands.Bot):
    async def setup_hook(self):
        for name in COG_MODULES:
            await self.load_extension(f"cogs.{name}")

bot = MusicBot(command_prefix="o!", intents=intents, help_command=None)

# Khi bot online
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.listening, name="o!play")
    )

# Lệnh help cơ bản
@bot.command(name="help")
async def help_cmd(ctx: commands.Context):
    embed = discord.Embed(title="o! commands", color=discord.Color.blurple())
    embed.add_field(name="o!play <tên|link>", value="Tìm top 5 + chọn bằng reaction, hoặc phát link YouTube", inline=False)
    embed.add_field(name="o!skip", value="Bỏ qua bài hiện tại", inline=True)
    embed.add_field(name="o!stop", value="Dừng và xoá hàng đợi", inline=True)
    embed.add_field(name="o!pause / o!resume", value="Tạm dừng / tiếp tục", inline=False)
    embed.add_field(name="o!queue", value="Xem hàng đợi", inline=True)
    embed.add_field(name="o!np", value="Đang phát", inline=True)
    embed.add_field(name="o!vol <0-200>", value="Âm lượng", inline=True)
    embed.add_field(name="o!join / o!leave", value="Gọi bot vào/ra kênh voice", inline=False)
    await ctx.reply(embed=embed)

# Chạy bot
if __name__ == "__main__":
    bot.run(TOKEN)
