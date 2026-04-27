from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

import discord
from discord.ext import commands


@dataclass
class GuildMasoNahoru:
    guild: discord.Guild
    user_ids: List[int] = field(default_factory=list)


class MasoNahoruManager:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._guilds: Dict[int, GuildMasoNahoru] = {}

    def get_guild(self, guild: discord.Guild) -> GuildMasoNahoru:
        if guild.id not in self._guilds:
            self._guilds[guild.id] = GuildMasoNahoru(guild)
        return self._guilds[guild.id]

    def add(self, guild: discord.Guild, member_id: int) -> bool:
        gm = self.get_guild(guild)
        if member_id in gm.user_ids:
            return False
        gm.user_ids.append(member_id)
        return True

    def remove(self, guild: discord.Guild, member_id: int) -> bool:
        gm = self.get_guild(guild)
        try:
            gm.user_ids.remove(member_id)
            return True
        except ValueError:
            return False

    def clear(self, guild: discord.Guild) -> None:
        gm = self.get_guild(guild)
        gm.user_ids.clear()

    def list_ids(self, guild: discord.Guild) -> List[int]:
        gm = self.get_guild(guild)
        return list(gm.user_ids)

    def build_embed(
        self,
        guild: discord.Guild,
        *,
        title: str = "🥩 Maso nahoru seznam (Ocasníkovi listy)",
        color: discord.Color = discord.Color.purple(),
        empty_text: str = "Seznam je zatím prázdný.",
    ) -> discord.Embed:
        ids = self.list_ids(guild)

        embed = discord.Embed(title=title, color=color)

        if not ids:
            embed.description = empty_text
            return embed

        lines: List[str] = []
        for i, uid in enumerate(ids, start=1):
            member: Optional[discord.Member] = guild.get_member(uid)
            mention = member.mention if member else f"<@{uid}>"
            lines.append(f"`{i}.` {mention}")

        # Keep description within Discord limits (4096 chars)
        text = "\n".join(lines)
        if len(text) > 4096:
            # Try a conservative truncation
            safe_lines: List[str] = []
            total = 0
            remaining = 0
            for idx, line in enumerate(lines):
                # +1 for newline
                new_total = total + len(line) + (1 if safe_lines else 0)
                if new_total > 3950:
                    remaining = len(lines) - idx
                    break
                safe_lines.append(line)
                total = new_total
            text = "\n".join(safe_lines)
            if remaining:
                text += f"\n\n*…a ještě {remaining} dalších*"

        embed.description = text
        embed.set_footer(text=f"Celkem: {len(ids)}")
        return embed


def get_manager(bot: commands.Bot) -> MasoNahoruManager:
    if not hasattr(bot, "maso_nahoru"):
        bot.maso_nahoru = MasoNahoruManager(bot)
    return bot.maso_nahoru
