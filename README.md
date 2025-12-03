# Discord Boost Notification Bot

A production-ready Discord bot that automatically tracks server boost levels across multiple servers and sends professional, visually appealing notifications to the bot owner when boost levels change. Built with performance optimizations including parallel processing, debounced file I/O, and efficient data structures.

## Overview

### What It Does

The Discord Boost Notification Bot monitors Discord server boost levels (Level 0-3) for configured servers and sends real-time notifications via DM when boost levels change. It performs automated hourly checks and maintains a persistent history of boost levels.

### Why It Exists

Server administrators and community managers need to track boost levels across multiple servers to:
- Monitor community engagement and support
- React quickly to boost level changes
- Track boost progression over time
- Maintain awareness of server status without manual checking

### Key Concepts

- **Boost Level**: Discord's tiered system (0-3) based on active boost count
- **Guild**: A Discord server
- **Owner**: The bot owner who receives notifications
- **Tracking**: Monitoring boost levels for specified servers
- **Debounced Save**: Batched file writes to reduce I/O overhead

## Features

### Core Functionality
- ✅ Tracks boost levels for specified servers
- ✅ Hourly automatic checks
- ✅ Sends DM notifications to bot owner when boost levels change
- ✅ Stores boost history in JSON file
- ✅ Supports multiple servers

### Professional Design
- 🎨 **Marketable Notifications**: Beautiful, professional Discord embeds with color-coded alerts
- 📊 **Visual Progress Bars**: Real-time progress indicators showing advancement to next boost level
- 🖼️ **Server Branding**: Automatic server icon integration for instant recognition
- 📈 **Clear Analytics**: Detailed statistics including boost counts, level descriptions, and member counts
- 🏷️ **Professional Branding**: Custom footer with bot branding for a polished appearance
- 🎯 **Smart Color Coding**: Green for upgrades, red for decreases - instantly recognizable status

## Setup Instructions

### 1. Create a Discord Bot

1. Go to https://discord.com/developers/applications
2. Click "New Application" and give it a name
3. Go to the "Bot" section
4. Click "Add Bot" and confirm
5. Under "Token", click "Reset Token" and copy the token
6. Enable "Message Content Intent" under "Privileged Gateway Intents"
7. Save changes

### 2. Invite Bot to Your Servers

1. Go to the "OAuth2" → "URL Generator" section
2. Select the "bot" scope
3. Select the "Read Messages/View Channels" permission (minimum)
4. Copy the generated URL and open it in your browser
5. Select the servers you want to track and authorize the bot

### 3. Get Your User ID

1. Enable Developer Mode in Discord:
   - User Settings → Advanced → Enable Developer Mode
2. Right-click your profile and select "Copy ID"
3. This is your `DISCORD_BOT_OWNER_ID`

### 4. Get Server IDs

1. Enable Developer Mode (if not already enabled)
2. Right-click each server you want to track
3. Select "Copy Server ID"
4. Collect all server IDs you want to track

### 5. Configure Environment Variables

1. Create a `.env` file in this directory:
   ```bash
   # Copy this template and fill in your values
   DISCORD_BOT_TOKEN=your_bot_token_here
   DISCORD_BOT_OWNER_ID=your_user_id_here
   DISCORD_TRACKED_GUILDS=123456789012345678,987654321098765432
   ```

2. Fill in:
   - `DISCORD_BOT_TOKEN`: Your bot token from step 1
   - `DISCORD_BOT_OWNER_ID`: Your user ID from step 3
   - `DISCORD_TRACKED_GUILDS`: Comma-separated list of server IDs from step 4

### 6. Install Dependencies

```bash
pip install discord.py python-dotenv
```

Or install from requirements file if available:
```bash
pip install -r requirements.txt
```

### 7. Run the Bot

**Windows:**
- Double-click `run_bot.bat` to start the bot
- Or run from command prompt: `run_bot.bat`

**Linux/Mac:**
```bash
python discord_bot.py
```

Or use the convenience script:
```bash
python run_bot.py
```

## Architecture

### System Design

The bot is built with a two-class architecture:

1. **BoostTracker**: Manages data persistence and boost level history
   - Handles JSON file I/O with debounced async saves
   - Provides O(1) lookups for previous boost levels
   - Implements dirty flag tracking for efficient writes

2. **BoostNotificationBot**: Main bot class extending `discord.Client`
   - Manages Discord API interactions
   - Handles parallel guild checking via `asyncio.gather()`
   - Sends formatted notification embeds

### Data Flow

```
1. Bot starts → Loads boost history from JSON
2. Hourly task triggers → Fetches all tracked guilds
3. Parallel checks → Each guild checked concurrently
4. Compare levels → Current vs previous boost level
5. If changed → Send notification + update storage
6. Debounced save → Batch writes to reduce I/O
```

### Performance Optimizations

- **Parallel Processing**: Guild checks run concurrently using `asyncio.gather()`
- **Debounced I/O**: File writes batched with 1-second debounce
- **Set-based Lookups**: O(1) guild membership testing
- **Cached Data**: Level info cached in memory to avoid repeated allocations
- **Efficient String Building**: Optimized progress bar generation

See [PERFORMANCE_OPTIMIZATIONS.md](PERFORMANCE_OPTIMIZATIONS.md) for detailed performance analysis.

## How It Works

### Boost Levels

Discord servers have boost levels based on the number of active boosts:
- **Level 0**: 0 boosts - No special perks
- **Level 1**: 2+ boosts - Basic perks (custom emoji, animated server icon)
- **Level 2**: 7+ boosts - Enhanced perks (server banner, invite splash)
- **Level 3**: 14+ boosts - Maximum perks (384kbps audio, custom server banner)

### Tracking Mechanism

1. **Initialization**: Bot loads previous boost levels from `data/boost_data.json`
2. **Hourly Checks**: Background task runs every hour to check all tracked servers
3. **Parallel Processing**: All guild checks execute concurrently for speed
4. **Change Detection**: Compares current level with stored previous level
5. **Notification**: Sends DM only when level actually changes
6. **Persistence**: Updates stored data with debounced async saves

### Notification Logic

- **First Check**: Logs initial level but doesn't send notification (no previous level to compare)
- **Level Change**: Sends notification with before/after comparison
- **No Change**: Logs at debug level, no notification sent
- **Error Handling**: Gracefully handles missing guilds, API errors, and DM failures

### Notifications

Notifications are sent as professional, visually appealing Discord embeds via DM to the bot owner. Each notification includes:

**Visual Features:**
- 🎨 Professional color-coded design (green for increases, red for decreases)
- 🖼️ Server icon thumbnail
- 📊 Visual progress bar showing boost progress to next level
- 📈 Clear level comparison with visual indicators
- 🏷️ Branded footer with bot information

**Information Provided:**
- Server name and icon
- Previous and current boost levels with clear comparison
- Total number of active boosts
- Progress bar showing advancement to next level
- Level descriptions (what each level unlocks)
- Server statistics (member count, server ID)
- Timestamp of the change

**Example Notification Structure:**
```
📈 Server Boost Level Update
[Server Name]

🎯 Boost Level: Level 1 → Level 2 ▲
📊 Current Statistics: 7 active boosts • Enhanced perks
📈 Progress: [Visual progress bar with percentage]
ℹ️ Server Information: Member count, Server ID
```

## Troubleshooting

### Bot doesn't respond / No notifications

1. **Check bot is online**: The bot should show as "Online" in Discord
2. **Check bot is in the server**: The bot must be a member of the tracked servers
3. **Check DMs are enabled**: Make sure you haven't blocked the bot
4. **Check logs**: Look for error messages in the console output
5. **Verify server IDs**: Make sure the server IDs in `.env` are correct

### "Cannot send DM to owner"

- The bot owner may have DMs disabled from server members
- Try sending a DM to the bot first, or adjust your privacy settings

### "Guild not found"

- The bot may have been removed from the server
- Verify the bot is still in the server and has the correct permissions

## API Documentation

### BoostTracker Class

Manages boost level data persistence and retrieval.

#### Methods

**`__init__(data_file: str = "data/boost_data.json")`**
- Initializes tracker with data file path
- Automatically creates data directory if missing
- Loads existing data from JSON file

**`get_previous_boost_level(guild_id: int) -> Optional[int]`**
- Returns the previously recorded boost level for a guild
- Returns `None` if guild has no previous data
- O(1) lookup time

**`update_boost_level(guild_id: int, boost_level: int, guild_name: str)`**
- Synchronous update with immediate save
- Use for one-off updates outside async context

**`update_boost_level_async(guild_id: int, boost_level: int, guild_name: str)`**
- Async update with debounced save (recommended)
- Batches rapid updates to reduce file I/O
- Automatically cancels pending saves if new update arrives

**`flush()`**
- Forces immediate save if data is dirty
- Call before shutdown to ensure data persistence

### BoostNotificationBot Class

Main bot class that extends `discord.Client`.

#### Constructor

**`__init__(owner_id: int, tracked_guilds: list, *args, **kwargs)`**

Parameters:
- `owner_id` (int): Discord user ID of bot owner (receives notifications)
- `tracked_guilds` (list): List of guild IDs to track (strings or ints)
- `*args, **kwargs`: Passed to `discord.Client` constructor

#### Key Methods

**`get_boost_level(guild: discord.Guild) -> int`**
- Calculates current boost level from guild's premium subscription count
- Returns 0-3 based on boost thresholds
- Pure function, no side effects

**`check_guild_boost(guild: discord.Guild) -> None`**
- Checks single guild's boost level
- Compares with previous level
- Sends notification if changed
- Updates stored data

**`send_boost_notification(guild: discord.Guild, previous_level: int, current_level: int) -> None`**
- Creates and sends Discord embed notification
- Handles color coding (green for increase, red for decrease)
- Includes progress bar, statistics, and server info
- Gracefully handles DM failures

**`check_boosts() -> None`** (Task Loop)
- Hourly background task
- Processes all tracked guilds in parallel
- Logs results and flushes data

#### Event Handlers

**`on_ready()`**
- Fetches owner user object
- Logs tracked guilds
- Called when bot connects to Discord

**`on_guild_join(guild: discord.Guild)`**
- Triggers immediate check for newly joined tracked guilds
- Flushes data to ensure persistence

**`on_guild_remove(guild: discord.Guild)`**
- Logs warning when removed from tracked guild
- Helps identify configuration issues

## Usage Examples

### Basic Usage

```python
import asyncio
from discord_bot import BoostNotificationBot

async def main():
    bot = BoostNotificationBot(
        owner_id=123456789012345678,
        tracked_guilds=["987654321098765432", "111222333444555666"]
    )
    await bot.start("YOUR_BOT_TOKEN")

asyncio.run(main())
```

### Custom Data File Location

```python
from discord_bot import BoostTracker, BoostNotificationBot

# Custom tracker with different data file
tracker = BoostTracker(data_file="custom/path/boosts.json")

# Or modify bot to use custom tracker
class CustomBot(BoostNotificationBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tracker = BoostTracker(data_file="custom/path/boosts.json")
```

### Environment Configuration

```bash
# .env file
DISCORD_BOT_TOKEN=your_token_here
DISCORD_BOT_OWNER_ID=123456789012345678
DISCORD_TRACKED_GUILDS=111222333444555666,222333444555666777,333444555666777888
```

### Running with Custom Check Interval

```python
from discord_bot import BoostNotificationBot

class CustomIntervalBot(BoostNotificationBot):
    @tasks.loop(hours=0.5)  # Check every 30 minutes
    async def check_boosts(self):
        await super().check_boosts()
```

## Best Practices

### Configuration

1. **Environment Variables**: Always use `.env` file, never hardcode tokens
2. **Guild IDs**: Use Developer Mode to get accurate guild IDs
3. **Owner ID**: Verify owner ID is correct to receive notifications
4. **Multiple Servers**: Use comma-separated list, no spaces around commas

### Performance

1. **Debounced Saves**: Use `update_boost_level_async()` in async contexts
2. **Parallel Processing**: Already implemented, but avoid blocking operations
3. **Data Persistence**: Call `flush()` before shutdown in custom implementations
4. **Error Handling**: Bot handles errors gracefully, but monitor logs

### Monitoring

1. **Logs**: Check console output for warnings and errors
2. **Data File**: Periodically verify `data/boost_data.json` is updating
3. **Notifications**: Test with a small change to verify DM delivery
4. **Guild Status**: Monitor "Guild not found" warnings

### Security

1. **Token Security**: Never commit `.env` file to version control
2. **Permissions**: Bot only needs minimal permissions (read guild info)
3. **Rate Limits**: Bot respects Discord rate limits automatically
4. **Data Privacy**: Boost data stored locally, not sent to external services

## Common Pitfalls

### ❌ Not Receiving Notifications

**Problem**: Bot runs but no DMs received

**Solutions**:
- Verify `DISCORD_BOT_OWNER_ID` is correct (use Developer Mode)
- Check if DMs are disabled from server members
- Ensure bot is actually in the tracked servers
- Check console logs for "Cannot send DM" errors

### ❌ "Guild not found" Warnings

**Problem**: Bot can't find tracked guilds

**Solutions**:
- Verify bot is invited to the servers
- Check guild IDs are correct (no typos)
- Ensure bot hasn't been removed from servers
- Verify bot has necessary permissions

### ❌ Data Not Persisting

**Problem**: Boost data resets on restart

**Solutions**:
- Check `data/` directory is writable
- Verify file permissions
- Ensure `flush()` is called on shutdown
- Check for JSON parsing errors in logs

### ❌ High CPU/Memory Usage

**Problem**: Bot uses excessive resources

**Solutions**:
- Reduce number of tracked guilds if needed
- Check for memory leaks in custom code
- Verify debounced saves are working (check logs)
- Consider increasing check interval for many guilds

### ❌ Rate Limit Errors

**Problem**: Discord API rate limit errors

**Solutions**:
- Bot handles rate limits automatically
- If persistent, reduce check frequency
- Check for other bots using same token
- Verify bot isn't making excessive API calls

## Error Handling

The bot implements comprehensive error handling:

- **File I/O Errors**: Logged, bot continues running
- **API Errors**: Caught and logged, individual guild checks don't fail entire batch
- **DM Failures**: Logged with specific error type (Forbidden, etc.)
- **Missing Guilds**: Warned but don't stop processing
- **JSON Parsing**: Falls back to empty dict on corruption

All errors are logged with appropriate levels (ERROR, WARNING, INFO, DEBUG).

## Files

- `discord_bot.py`: Main bot implementation (397 lines)
- `run_bot.py`: Convenience Python script to run the bot
- `run_bot.bat`: Windows batch script launcher (double-click to run)
- `requirements.txt`: Python dependencies
- `README.md`: This documentation file
- `PERFORMANCE_OPTIMIZATIONS.md`: Detailed performance analysis
- `data/boost_data.json`: Stored boost level data (auto-generated)
- `.env`: Your configuration file (create this, not in git)

## Stopping the Bot

Press `Ctrl+C` in the terminal to gracefully shut down the bot. The bot will:
1. Cancel the hourly check task
2. Flush any pending data writes
3. Close Discord connection cleanly
4. Log shutdown message

## Dependencies

- **discord.py** (>=2.3.0): Discord API library
- **python-dotenv** (>=1.0.0): Environment variable management

## License

This bot is provided as-is for use in tracking Discord server boost levels.

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review console logs for error messages
3. Verify configuration matches setup instructions
4. Check Discord API status if persistent issues

