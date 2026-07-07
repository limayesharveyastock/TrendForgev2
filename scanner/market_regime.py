"""
market_regime.py
----------------------------------------------------------
TrendForge Market Regime Detection Engine

Features
--------
- Bull Market Detection
- Bear Market Detection
- Sideways Market Detection
- High Volatility Detection
- Low Volatility Detection
- Market Strength Score
- Risk Multiplier
- Strategy Recommendation
"""

from dataclasses import dataclass
from enum import Enum


# ==========================================================
# MARKET REGIMES
# ==========================================================

class MarketRegime(Enum):

    BULL = "Bull Market"

    BEAR = "Bear Market"

    SIDEWAYS = "Sideways Market"

    HIGH_VOLATILITY = "High Volatility"

    LOW_VOLATILITY = "Low Volatility"


# ==========================================================
# INPUT
# ==========================================================

@dataclass
class MarketData:

    index_price: float

    ema50: float

    ema200: float

    adx: float

    atr_percent: float

    vix: float

    advance_decline_ratio: float


# ==========================================================
# RESULT
# ==========================================================

@dataclass
class RegimeResult:

    regime: MarketRegime

    confidence: float

    risk_multiplier: float

    strategy: str

    score: int


# ==========================================================
# ENGINE
# ==========================================================

class MarketRegimeDetector:

    def __init__(self):

        self.high_vix = 20

        self.low_vix = 13

        self.strong_adx = 25

    # ------------------------------------------------------

    def detect(
        self,
        data: MarketData
    ) -> RegimeResult:

        score = 0

        if data.index_price > data.ema50:

            score += 15

        else:

            score -= 15

        if data.ema50 > data.ema200:

            score += 30

        else:

            score -= 30

        if data.adx >= self.strong_adx:

            score += 20

        if data.advance_decline_ratio > 1:

            score += 15

        else:

            score -= 15

        # High Volatility
        if data.vix >= self.high_vix:

            return RegimeResult(

                regime=MarketRegime.HIGH_VOLATILITY,

                confidence=90,

                risk_multiplier=0.50,

                strategy="Reduce Position Size | Trade Breakouts Only",

                score=score

            )

        # Low Volatility
        if data.vix <= self.low_vix and data.atr_percent < 1:

            return RegimeResult(

                regime=MarketRegime.LOW_VOLATILITY,

                confidence=85,

                risk_multiplier=0.75,

                strategy="Range Trading | Mean Reversion",

                score=score

            )

        # Bull
        if score >= 40:

            return RegimeResult(

                regime=MarketRegime.BULL,

                confidence=min(100, score),

                risk_multiplier=1.20,

                strategy="Trend Following | Buy Pullbacks",

                score=score

            )

        # Bear
        if score <= -40:

            return RegimeResult(

                regime=MarketRegime.BEAR,

                confidence=min(100, abs(score)),

                risk_multiplier=0.70,

                strategy="Short Selling | Buy Puts",

                score=score

            )

        # Sideways
        return RegimeResult(

            regime=MarketRegime.SIDEWAYS,

            confidence=70,

            risk_multiplier=0.80,

            strategy="Range Trading",

            score=score

        )

    # ------------------------------------------------------

    def recommended_position_size(
        self,
        base_quantity: int,
        regime: RegimeResult
    ) -> int:

        return max(
            1,
            int(base_quantity * regime.risk_multiplier)
        )

    # ------------------------------------------------------

    def summary(
        self,
        result: RegimeResult
    ):

        return {

            "Market Regime": result.regime.value,

            "Confidence": result.confidence,

            "Risk Multiplier": result.risk_multiplier,

            "Recommended Strategy": result.strategy,

            "Market Score": result.score

        }