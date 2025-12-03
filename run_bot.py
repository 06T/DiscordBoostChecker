#!/usr/bin/env python3
"""Convenience script to run the Discord boost notification bot."""

import sys
import asyncio
from pathlib import Path

current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from discord_bot import main

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Error running bot: {e}", file=sys.stderr)
        sys.exit(1)

