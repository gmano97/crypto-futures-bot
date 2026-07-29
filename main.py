import ccxt
import pandas as pd
import requests
import time

# ==========================================
# 1. TELEGRAM & API CREDENTIALS
# ==========================================
TELEGRAM_BOT_TOKEN = '8977777997:AAEvwcbsgOK0Gafij9rMx87_lQMeFUsI0C4'
TELEGRAM_CHAT_ID = '1371553688'

BINANCE_API_KEY = 'linLKfb5vlCVsrSwhY3GgUA9yR3jX8BeQlL5UqI3xDZeLqxo08wAx4st2aiVvrkS'
BINANCE_SECRET_KEY = '4Pwys4qWhublkEPUmoDKmF5Tfh818ji1SR4wjuWnVh1SEGION4824tqZjuSR4Ep3'  # உங்களின் Secret Key-ஐ இங்கு போடவும்

# ==========================================
# 2. FULL 150 FUTURES COINS LIST
# ==========================================
COINS_LIST = [
    # Top Market Cap & High Volume
    'BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'XRP/USDT',
    'ADA/USDT', 'DOGE/USDT', 'AVAX/USDT', 'LINK/USDT', 'SUI/USDT',
    'DOT/USDT', 'POL/USDT', 'LTC/USDT', 'BCH/USDT', 'NEAR/USDT',
    'APT/USDT', 'ARB/USDT', 'OP/USDT', 'INJ/USDT', 'TIA/USDT',

    # Screenshot Gainers & High Movers
    'ON/USDT', 'BTW/USDT', 'UB/USDT', 'BEAT/USDT', 'EUL/USDT', 
    'SOXS/USDT', 'BOT/USDT', 'ZIL/USDT', 'HOLO/USDT', 'HK1810/USDT', 
    'FLOW/USDT', 'ZEST/USDT', 'SOON/USDT', 'IRYS/USDT', 'TAKE/USDT', 
    'PROM/USDT', 'POPMART/USDT', 'PHAROS/USDT', 'SLX/USDT', 'TER/USDT', 
    'LIT/USDT', '1000CHEEMS/USDT', 'OPEN/USDT', 'IBM/USDT', 'NOW/USDT', 
    'ADBE/USDT', 'GPS/USDT', 'KOMA/USDT', 'TURTLE/USDT', 'CRM/USDT', 
    'SONY/USDT', 'KMNO/USDT', 'TUT/USDT',

    # AI & Big Data Tokens
    'RENDER/USDT', 'FET/USDT', 'TAO/USDT', 'WLD/USDT', 'ARKM/USDT',
    'AGIX/USDT', 'OCEAN/USDT', 'AKT/USDT', 'NMR/USDT', 'GRT/USDT',

    # High Volatility Meme Coins
    '1000PEPE/USDT', '1000SHIB/USDT', '1000FLOKI/USDT', 'WIF/USDT', '1000BONK/USDT',
    '1000SATS/USDT', 'MEME/USDT', 'PEOPLE/USDT', 'MYRO/USDT', 'POPCAT/USDT',
    'BRETT/USDT', 'MEW/USDT', 'TURBO/USDT', 'NEIRO/USDT', 'BOME/USDT',

    # Layer 1 & Layer 2 Protocols
    'SEI/USDT', 'STX/USDT', 'ATOM/USDT', 'FTM/USDT', 'ALGO/USDT', 
    'EGLD/USDT', 'KAS/USDT', 'ROSE/USDT', 'STRK/USDT', 'MANTA/USDT', 
    'ALT/USDT', 'METIS/USDT', 'ZK/USDT', 'BLAST/USDT', 'RON/USDT',
    'ZETA/USDT', 'SGLD/USDT', 'DYM/USDT', 'PYTH/USDT', 'TNSR/USDT',

    # DeFi & Yield Tokens
    'UNI/USDT', 'AAVE/USDT', 'MKR/USDT', 'CRV/USDT', 'LDO/USDT',
    'PENDLE/USDT', 'JUP/USDT', 'RUNE/USDT', 'ENA/USDT', 'SNX/USDT',
    'COMP/USDT', 'DYDX/USDT', '1INCH/USDT', 'CAKE/USDT', 'RAY/USDT',
    'CVX/USDT', 'SUSHI/USDT', 'KAVA/USDT', 'FXS/USDT', 'GMX/USDT',

    # Gaming, Metaverse & NFT
    'GALA/USDT', 'SAND/USDT', 'MANA/USDT', 'IMX/USDT', 'BEAM/USDT',
    'PIXEL/USDT', 'YGG/USDT', 'AXS/USDT', 'ILV/USDT', 'ALICE/USDT',
    'ENJ/USDT', 'MAGIC/USDT', 'HERO/USDT', 'TLM/USDT', 'DAR/USDT',

    # High Volatility & Momentum Movers
    'ORDI/USDT', 'TRB/USDT', 'BLUR/USDT', 'GAS/USDT', 'ARK/USDT', 
    'LOOM/USDT', 'BIGTIME/USDT', 'NOT/USDT', 'TON/USDT', 'IO/USDT', 
    'ATH/USDT', 'ZRO/USDT', 'LISTA/USDT', 'BB/USDT', 'OM/USDT', 
    'AERO/USDT', 'CELO/USDT', 'FIL/USDT', 'JTO/USDT', 'DRIFT/USDT', 
    'ETHFI/USDT', 'ZEN/USDT', 'SSV/USDT', 'RNDR/USDT', 'SUPER/USDT'
]

TIMEFRAME = '1h'
RECOMMENDED_LEVERAGE = "3x - 5x (Isolated)"

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

def calculate_indicators(df):
    df['ema200'] = df['close'].ewm(span=200, adjust=False).mean()
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))

    exp1 = df['close'].ewm(span=12, adjust=False).mean()
    exp2 = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = exp1 - exp2
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()

    sma = df['close'].rolling(window=20).mean()
    std = df['close'].rolling(window=20).std()
    df['bb_upper'] = sma + (std * 2)
    df['bb_lower'] = sma - (std * 2)

    df['vol_sma'] = df['volume'].rolling(window=20).mean()
    df['high_20'] = df['high'].shift(1).rolling(20).max()
    df['low_20'] = df['low'].shift(1).rolling(20).min()
    return df

def analyze_futures_market():
    exchange = ccxt.binance({
        'apiKey': BINANCE_API_KEY,
        'secret': BINANCE_SECRET_KEY,
        'enableRateLimit': True,
        'options': {'defaultType': 'future'}
    })
    
    for symbol in COINS_LIST:
        try:
            bars = exchange.fetch_ohlcv(symbol, timeframe=TIMEFRAME, limit=200)
            df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
            df = calculate_indicators(df)

            price = df['close'].iloc[-1]
            prev_price = df['close'].iloc[-2]
            ema200 = df['ema200'].iloc[-1]
            rsi = df['rsi'].iloc[-1]
            macd_val = df['macd'].iloc[-1]
            macd_sig = df['macd_signal'].iloc[-1]
            bb_lower = df['bb_lower'].iloc[-1]
            bb_upper = df['bb_upper'].iloc[-1]
            volume = df['volume'].iloc[-1]
            vol_sma = df['vol_sma'].iloc[-1]
            high_20 = df['high_20'].iloc[-1]
            low_20 = df['low_20'].iloc[-1]

            is_uptrend = price > ema200
            is_downtrend = price < ema200
            rsi_oversold = rsi < 42
            rsi_overbought = rsi > 58
            macd_bullish = macd_val > macd_sig
            macd_bearish = macd_val < macd_sig
            near_bb_lower = price <= (bb_lower * 1.008)
            near_bb_upper = price >= (bb_upper * 0.992)
            good_volume = volume > (vol_sma * 0.8)

            # 5-Strategy LONG
            if is_uptrend and rsi_oversold and macd_bullish and near_bb_lower and good_volume:
                sl, tp1, tp2 = price * 0.985, price * 1.03, price * 1.05
                send_telegram_msg(f"🟢 *5-STRATEGY LONG SIGNAL*\n\n📌 *Coin:* `{symbol}`\n⚡ *Leverage:* {RECOMMENDED_LEVERAGE}\n📌 *Entry:* ${price:.4f}\n🛡️ *SL:* ${sl:.4f}\n🎯 *TP1:* ${tp1:.4f}\n🎯 *TP2:* ${tp2:.4f}")

            # 5-Strategy SHORT
            elif is_downtrend and rsi_overbought and macd_bearish and near_bb_upper and good_volume:
                sl, tp1, tp2 = price * 1.015, price * 0.97, price * 0.95
                send_telegram_msg(f"🔴 *5-STRATEGY SHORT SIGNAL*\n\n📌 *Coin:* `{symbol}`\n⚡ *Leverage:* {RECOMMENDED_LEVERAGE}\n📌 *Entry:* ${price:.4f}\n🛡️ *SL:* ${sl:.4f}\n🎯 *TP1:* ${tp1:.4f}\n🎯 *TP2:* ${tp2:.4f}")

            # Breakout Signals
            is_bullish_breakout = (price > high_20) and (prev_price <= high_20) and (price > ema200) and (volume > vol_sma * 1.5)
            is_bearish_breakout = (price < low_20) and (prev_price >= low_20) and (price < ema200) and (volume > vol_sma * 1.5)

            if is_bullish_breakout:
                sl, tp1, tp2 = price * 0.98, price * 1.04, price * 1.08
                send_telegram_msg(f"🚀 *UPTREND BREAKOUT SIGNAL*\n\n📌 *Coin:* `{symbol}`\n📌 *Entry:* ${price:.4f}\n🛡️ *SL:* ${sl:.4f}\n🎯 *TP1:* ${tp1:.4f}\n🎯 *TP2:* ${tp2:.4f}")

            elif is_bearish_breakout:
                sl, tp1, tp2 = price * 1.02, price * 0.96, price * 0.92
                send_telegram_msg(f"💥 *DOWNTREND BREAKOUT SIGNAL*\n\n📌 *Coin:* `{symbol}`\n📌 *Entry:* ${price:.4f}\n🛡️ *SL:* ${sl:.4f}\n🎯 *TP1:* ${tp1:.4f}\n🎯 *TP2:* ${tp2:.4f}")

            time.sleep(0.3)
        except Exception as e:
            print(f"Error {symbol}: {e}")

if __name__ == "__main__":
    analyze_futures_market()
