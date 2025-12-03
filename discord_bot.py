"""
Discord Boost Notification Bot

Tracks server boost levels and notifies the bot owner when changes occur.
Performs hourly checks on configured servers.
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

import discord
from discord.ext import tasks

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BoostTracker:
    """Manages boost level tracking and storage."""
    
    def __init__(self, data_file: str = "data/boost_data.json"):
        self.data_file = Path(data_file)
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        self.boost_data: Dict[int, Dict] = self._load_data()
        self._dirty = False
        self._save_task = None
    
    def _load_data(self) -> Dict[int, Dict]:
        """Load boost data from JSON file."""
        if not self.data_file.exists():
            return {}
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {int(k): v for k, v in data.items()}
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Error loading boost data: {e}")
            return {}
    
    def _save_data(self):
        """Save boost data to JSON file."""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.boost_data, f, indent=2, ensure_ascii=False)
            self._dirty = False
        except Exception as e:
            logger.error(f"Error saving boost data: {e}")
    
    async def _debounced_save(self):
        """Debounced save to batch multiple rapid updates."""
        await asyncio.sleep(1)
        if self._dirty:
            self._save_data()
    
    def get_previous_boost_level(self, guild_id: int) -> Optional[int]:
        """Get the previously recorded boost level for a guild."""
        guild_data = self.boost_data.get(guild_id)
        if guild_data:
            return guild_data.get('boost_level', 0)
        return None
    
    def update_boost_level(self, guild_id: int, boost_level: int, guild_name: str):
        """Update the boost level for a guild."""
        self.boost_data[guild_id] = {
            'boost_level': boost_level,
            'guild_name': guild_name,
            'last_updated': datetime.utcnow().isoformat()
        }
        self._dirty = True
        self._save_data()
    
    async def update_boost_level_async(self, guild_id: int, boost_level: int, guild_name: str):
        """Update boost level with debounced async save."""
        self.boost_data[guild_id] = {
            'boost_level': boost_level,
            'guild_name': guild_name,
            'last_updated': datetime.utcnow().isoformat()
        }
        self._dirty = True
        
        if self._save_task and not self._save_task.done():
            self._save_task.cancel()
        
        self._save_task = asyncio.create_task(self._debounced_save())
    
    def flush(self):
        """Force immediate save if dirty."""
        if self._dirty:
            self._save_data()


class BoostNotificationBot(discord.Client):
    """Discord bot that tracks server boost levels and sends notifications."""
    
    def __init__(self, owner_id: int, tracked_guilds: list, *args, **kwargs):
        intents = discord.Intents.default()
        intents.guilds = True
        intents.members = True
        super().__init__(intents=intents, *args, **kwargs)
        
        self.owner_id = owner_id
        self.tracked_guild_ids = {int(gid) for gid in tracked_guilds}
        self.tracker = BoostTracker()
        self.owner: Optional[discord.User] = None
        self._level_info_cache = {
            0: ("None", "No active boosts"),
            1: ("Level 1", "2+ boosts • Basic perks"),
            2: ("Level 2", "7+ boosts • Enhanced perks"),
            3: ("Level 3", "14+ boosts • Maximum perks")
        }
    
    async def setup_hook(self):
        """Called when the bot is starting up."""
        self.check_boosts.start()
        logger.info("Boost check task started")
    
    async def on_ready(self):
        """Called when the bot is ready."""
        logger.info(f'{self.user} has logged in!')
        logger.info(f'Bot ID: {self.user.id}')
        
        self.owner = await self.fetch_user(self.owner_id)
        if self.owner:
            logger.info(f'Bot owner: {self.owner.name}#{self.owner.discriminator} ({self.owner_id})')
        else:
            logger.warning(f'Could not fetch owner user with ID {self.owner_id}')
        
        logger.info(f'Tracking {len(self.tracked_guild_ids)} server(s)')
        for guild_id in self.tracked_guild_ids:
            guild = self.get_guild(guild_id)
            if guild:
                logger.info(f'  - {guild.name} (ID: {guild_id})')
            else:
                logger.warning(f'  - Guild ID {guild_id} not found (bot may not be in this server)')
    
    def get_boost_level(self, guild: discord.Guild) -> int:
        """
        Get the current boost level of a guild.
        
        Boost levels:
        - Level 0: 0 boosts
        - Level 1: 2+ boosts
        - Level 2: 7+ boosts
        - Level 3: 14+ boosts
        """
        premium_subscription_count = guild.premium_subscription_count or 0
        
        if premium_subscription_count >= 14:
            return 3
        elif premium_subscription_count >= 7:
            return 2
        elif premium_subscription_count >= 2:
            return 1
        else:
            return 0
    
    async def check_guild_boost(self, guild: discord.Guild):
        """Check boost level for a single guild and notify if changed."""
        current_level = self.get_boost_level(guild)
        previous_level = self.tracker.get_previous_boost_level(guild.id)
        
        if previous_level is None:
            await self.tracker.update_boost_level_async(guild.id, current_level, guild.name)
            logger.info(
                f'Initial boost check for {guild.name}: Level {current_level} '
                f'({guild.premium_subscription_count} boosts)'
            )
            return
        
        if current_level != previous_level:
            await self.tracker.update_boost_level_async(guild.id, current_level, guild.name)
            await self.send_boost_notification(
                guild=guild,
                previous_level=previous_level,
                current_level=current_level
            )
        else:
            logger.debug(
                f'Boost check for {guild.name}: Level {current_level} '
                f'({guild.premium_subscription_count} boosts) - No change'
            )
    
    def get_boost_level_info(self, level: int) -> Tuple[str, str]:
        """Get boost level name and description."""
        return self._level_info_cache.get(level, ("Unknown", "Unknown level"))
    
    def get_boost_progress_bar(self, current_boosts: int) -> str:
        """Generate a visual progress bar for boost levels."""
        if current_boosts >= 14:
            return "████████████████████ MAX (Level 3)"
        
        if current_boosts < 2:
            next_threshold = 2
            progress = min(current_boosts / 2, 1.0)
        elif current_boosts < 7:
            next_threshold = 7
            progress = (current_boosts - 2) / 5
        else:
            next_threshold = 14
            progress = (current_boosts - 7) / 7
        
        filled = int(progress * 20)
        percentage = int(progress * 100)
        return f"{'█' * filled}{'░' * (20 - filled)} {percentage}% ({current_boosts}/{next_threshold})"
    
    async def send_boost_notification(
        self,
        guild: discord.Guild,
        previous_level: int,
        current_level: int
    ):
        """Send notification to bot owner about boost level change."""
        if not self.owner:
            logger.warning("Cannot send notification: owner not set")
            return
        
        current_boosts = guild.premium_subscription_count or 0
        
        if current_level > previous_level:
            direction_emoji = "📈"
            status_text = "Congratulations! Your server has reached a new boost level."
            color = discord.Color.from_rgb(46, 204, 113)
            change_indicator = "▲"
        else:
            direction_emoji = "📉"
            status_text = "Your server's boost level has decreased."
            color = discord.Color.from_rgb(231, 76, 60)
            change_indicator = "▼"
        
        prev_level_name, prev_level_desc = self.get_boost_level_info(previous_level)
        curr_level_name, curr_level_desc = self.get_boost_level_info(current_level)
        
        embed = discord.Embed(
            title=f"{direction_emoji} Server Boost Level Update",
            description=f"**{guild.name}**\n\n{status_text}",
            color=color,
            timestamp=datetime.utcnow()
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        level_comparison = (
            f"**{prev_level_name}** → **{curr_level_name}** {change_indicator}\n"
            f"`{previous_level}` → `{current_level}`"
        )
        embed.add_field(
            name="🎯 Boost Level",
            value=level_comparison,
            inline=False
        )
        
        stats_value = (
            f"**{current_boosts}** active boosts\n"
            f"{curr_level_desc}"
        )
        embed.add_field(
            name="📊 Current Statistics",
            value=stats_value,
            inline=True
        )
        
        progress_bar = self.get_boost_progress_bar(current_boosts)
        progress_value = f"```\n{progress_bar}\n```"
        embed.add_field(
            name="📈 Progress",
            value=progress_value,
            inline=True
        )
        
        member_count = guild.member_count or 0
        server_info = (
            f"🆔 Server ID: `{guild.id}`\n"
            f"👥 Members: `{member_count:,}`"
        )
        embed.add_field(
            name="ℹ️ Server Information",
            value=server_info,
            inline=False
        )
        
        embed.set_footer(
            text="Boost Tracker • Automated Monitoring",
            icon_url=self.user.avatar.url if self.user.avatar else None
        )
        
        try:
            await self.owner.send(embed=embed)
            logger.info(
                f"Sent boost notification to owner: {guild.name} "
                f"Level {previous_level} → {current_level}"
            )
        except discord.Forbidden:
            logger.error(
                f"Cannot send DM to owner (ID: {self.owner_id}). "
                "The bot owner may have DMs disabled."
            )
        except Exception as e:
            logger.error(f"Error sending notification: {e}", exc_info=True)
    
    @tasks.loop(hours=1)
    async def check_boosts(self):
        """Hourly task to check boost levels for all tracked guilds."""
        logger.info("Starting hourly boost check...")
        
        guilds = [self.get_guild(guild_id) for guild_id in self.tracked_guild_ids]
        valid_guilds = [g for g in guilds if g is not None]
        
        if not valid_guilds:
            logger.warning("No valid guilds found for boost check")
            return
        
        missing = len(self.tracked_guild_ids) - len(valid_guilds)
        if missing > 0:
            logger.warning(f"{missing} guild(s) not found (bot may have been removed)")
        
        await asyncio.gather(*[self.check_guild_boost(guild) for guild in valid_guilds], return_exceptions=True)
        
        self.tracker.flush()
        logger.info(f"Boost check complete. Checked {len(valid_guilds)}/{len(self.tracked_guild_ids)} server(s)")
    
    @check_boosts.before_loop
    async def before_check_boosts(self):
        """Wait until the bot is ready before starting the task."""
        await self.wait_until_ready()
        await asyncio.sleep(5)
    
    async def on_guild_join(self, guild: discord.Guild):
        """Called when the bot joins a new guild."""
        if guild.id in self.tracked_guild_ids:
            logger.info(f"Joined tracked guild: {guild.name}")
            await self.check_guild_boost(guild)
            self.tracker.flush()
    
    async def on_guild_remove(self, guild: discord.Guild):
        """Called when the bot is removed from a guild."""
        if guild.id in self.tracked_guild_ids:
            logger.warning(f"Removed from tracked guild: {guild.name}")
    
    async def close(self):
        """Cleanup when the bot is shutting down."""
        logger.info("Shutting down boost notification bot...")
        self.check_boosts.cancel()
        self.tracker.flush()
        await super().close()


async def main():
    """Main entry point for the bot."""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    bot_token = os.getenv('DISCORD_BOT_TOKEN')
    owner_id = int(os.getenv('DISCORD_BOT_OWNER_ID', '0'))
    tracked_guilds_str = os.getenv('DISCORD_TRACKED_GUILDS', '')
    
    if not bot_token:
        raise ValueError("DISCORD_BOT_TOKEN environment variable is required")
    
    if not owner_id:
        raise ValueError("DISCORD_BOT_OWNER_ID environment variable is required")
    
    if not tracked_guilds_str:
        raise ValueError("DISCORD_TRACKED_GUILDS environment variable is required")
    
    tracked_guilds = [gid.strip() for gid in tracked_guilds_str.split(',') if gid.strip()]
    
    if not tracked_guilds:
        raise ValueError("At least one guild ID must be provided in DISCORD_TRACKED_GUILDS")
    
    logger.info(f"Starting bot with owner ID: {owner_id}")
    logger.info(f"Tracking {len(tracked_guilds)} server(s)")
    
    bot = BoostNotificationBot(owner_id=owner_id, tracked_guilds=tracked_guilds)
    
    try:
        await bot.start(bot_token)
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    finally:
        await bot.close()


if __name__ == '__main__':
    asyncio.run(main())

