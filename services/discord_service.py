"""
TrendForge v2
Discord Alert Service
"""

from __future__ import annotations

import logging
from datetime import datetime
import requests

from services.config_service import ConfigService

logger = logging.getLogger(__name__)


class DiscordService:

    def __init__(self):

        self.config = ConfigService.load(
            "alerts.json"
        )

        self.discord = self.config["discord"]

    # ----------------------------------------------------
    # Enabled
    # ----------------------------------------------------

    def enabled(self):

        return (

            self.config["enabled"]

            and

            self.discord["enabled"]

            and

            self.discord["webhook_url"] != ""

        )

    # ----------------------------------------------------
    # Color
    # ----------------------------------------------------

    def color(
        self,
        signal,
    ):

        colors = {

            "STRONG BUY": 0x00FF00,

            "BUY": 0x0099FF,

            "WATCH": 0xFFD700,

            "SELL": 0xFF0000,

            "IGNORE": 0x808080,

        }

        return colors.get(
            signal,
            0x0099FF,
        )

    # ----------------------------------------------------
    # Embed
    # ----------------------------------------------------

    def create_embed(

        self,

        symbol,

        result,

        price,

        target=None,

        stoploss=None,

        timeframe="Daily",

        scanner="TrendForge",

    ):

        fields = [

            {

                "name": "Signal",

                "value": result.signal,

                "inline": True,

            },

            {

                "name": "Score",

                "value": f"{result.score}/100",

                "inline": True,

            },

            {

                "name": "Price",

                "value": f"₹ {price:.2f}",

                "inline": True,

            },

            {

                "name": "Scanner",

                "value": scanner,

                "inline": True,

            },

            {

                "name": "Timeframe",

                "value": timeframe,

                "inline": True,

            },

        ]

        if target is not None:

            fields.append({

                "name": "Target",

                "value": f"₹ {target:.2f}",

                "inline": True,

            })

        if stoploss is not None:

            fields.append({

                "name": "Stop Loss",

                "value": f"₹ {stoploss:.2f}",

                "inline": True,

            })

        if result.reasons:

            fields.append({

                "name": "Reasons",

                "value": "\n".join(

                    f"• {r}"

                    for r in result.reasons

                ),

                "inline": False,

            })

        embed = {

            "title": f"📈 {symbol}",

            "description": "TrendForge Trading Signal",

            "color": self.color(

                result.signal

            ),

            "fields": fields,

            "footer": {

                "text": datetime.now()

                .strftime(

                    "%d-%b-%Y %H:%M:%S"

                )

            }

        }

        return embed

    # ----------------------------------------------------
    # Send
    # ----------------------------------------------------

    def send(

        self,

        symbol,

        result,

        price,

        target=None,

        stoploss=None,

        timeframe="Daily",

        scanner="TrendForge",

    ):

        if not self.enabled():

            logger.warning(

                "Discord alerts disabled."

            )

            return False

        embed = self.create_embed(

            symbol,

            result,

            price,

            target,

            stoploss,

            timeframe,

            scanner,

        )

        payload = {

            "username":

            self.discord.get(

                "username",

                "TrendForge",

            ),

            "avatar_url":

            self.discord.get(

                "avatar_url",

                "",

            ),

            "embeds": [

                embed

            ],

        }

        try:

            response = requests.post(

                self.discord["webhook_url"],

                json=payload,

                timeout=self.discord.get(

                    "timeout",

                    10,

                ),

            )

            response.raise_for_status()

            logger.info(

                "Discord alert sent."

            )

            return True

        except Exception as exc:

            logger.exception(

                "Discord alert failed: %s",

                exc,

            )

            return False

    # ----------------------------------------------------
    # Test
    # ----------------------------------------------------

    def send_test(self):

        class Dummy:

            signal = "BUY"

            score = 95

            reasons = [

                "EMA Alignment",

                "20-Day Breakout",

                "MACD Bullish",

                "High RVOL",

            ]

        return self.send(

            symbol="TRENDFORGE",

            result=Dummy(),

            price=1000,

            target=1080,

            stoploss=970,

            timeframe="Daily",

            scanner="System Test",

        )

    # ----------------------------------------------------
    # Health
    # ----------------------------------------------------

    def health(self):

        return {

            "enabled":

            self.enabled(),

            "provider":

            "Discord",

            "configured":

            from config.settings import DISCORD_WEBHOOK

            ...

            requests.post(
             DISCORD_WEBHOOK,
             ...
            ) != "",
            }