import ccxt
import pandas as pd
import pandas_ta as ta
import requests
import time
import os
from flask import Flask
from threading import Thread

# ==========================================
# 1. KEEP-ALIVE WEB SERVER (For Render / UptimeRobot)
# ==========================================
app = Flask('')

@app.route('/')
def home():
    return "Crypto Futures Bot is Active & Running 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# ==========================================
# 2. API & TELEGRAM CREDENTIALS
# ==========================================
TELEGRAM_BOT_TOKEN = '8977777997:AAEvwcbsgOK0Gafij9rMx87_lQMeFUsI0C4'
TELEGRAM_CHAT_ID = '1371553688'

BINANCE_API_KEY = ''
BINANCE_SECRET_KEY = ''  # உங்களின் Secret Key-ஐ இங்கு போடவும்

# ==========================================
# 3. 140+ FUTURES COINS LIST
# ==========================================
COINS_LIST = [
    # Top Market Cap & High Volume
    'BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'XRP/USDT',
    'ADA/USDT', 'DOGE/USDT', 'AVAX/USDT', 'LINK/USDT', 'SUI/USDT',
    'DOT/USDT', 'POL/USDT', 'LTC/USDT', 'BCH/USDT', 'NEAR/USDT',
    'APT/USDT', 'ARB/USDT', 'OP/USDT', 'INJ/USDT', 'TIA/USDT',

    # Screenshot Gainers & Movers
    'ON/USDT', 'BTW/USDT', 'UB/USDT', 'BEAT/USDT', 'EUL/USDT', 
    'SOXS/USDT', 'BOT/USDT', 'ZIL/USDT', 'HOLO/USDT', 'HK1810/USDT', 
    'FLOW/USDT', 'ZEST/USDT', 'SOON/USDT', 'IRYS/USDT', 'TAKE/USDT', 
    'PROM/USDT', 'POPMART/USDT', 'PHAROS/USDT', 'SLX/USDT', 'TER/USDT', 
    'LIT/USDT', '1000CHEEMS/USDT', 'OPEN/USDT', 'IBM/USDT', 'NOW/USDT', 
    'ADBE/USDT', 'GPS/USDT', 'KOMA/USDT', 'TURTLE/USDT', 'CRM/USDT', 
    'SONY/USDT', 'KMNO/USDT', 'TUT/USDT',

    # AI & Big Data Tokens
    'RENDER/USDT', 'FET/USDT', 'TAO/USDT', 'WLD/USDT', 'ARKM/USDT',
    'AGIX/USDT', 'OCEAN/USDT', 'AKT/USDT', 'NMR/USDT',

    # High Volatility Meme Coins (Binance Futures Symbols)
    '1000PEPE/USDT', '1000SHIB/USDT', '1000FLOKI/USDT', 'WIF/USDT', '1000BONK/USDT',
    '1000SATS/USDT', 'MEME/USDT', 'PEOPLE/USDT', 'MYRO/USDT', 'POPCAT/USDT',

    # Layer 1 & Layer 2 Protocols
    'SEI/USDT', 'STX/USDT', 'ATOM/USDT', 'FTM/USDT', 'ALGO/USDT', 
    'EGLD/USDT', 'KAS/USDT', 'ROSE/USDT', 'STRK/USDT', 'MANTA/USDT', 
    'ALT/USDT', 'METIS/USDT', 'ZK/USDT', 'BLAST/USDT',

    # DeFi & Yield Tokens
    'UNI/USDT', 'AAVE/USDT', 'MKR/USDT', 'CRV/USDT', 'LDO/USDT',
    'PENDLE/USDT', 'JUP/USDT', 'RUNE/USDT', 'ENA/USDT', 'SNX/USDT',
    'COMP/USDT', 'DYDX/USDT', '1INCH/USDT', 'CAKE/USDT', 'RAY/USDT',

    # Gaming, Metaverse & NFT
    'GALA/USDT', 'SAND/USDT', 'MANA/USDT', 'IMX/USDT', 'BEAM/USDT',
    'PIXEL/USDT', 'YGG/USDT', 'AXS/USDT', 'ILV/USDT', 'ALICE/USDT',

    # High Volatility & Momentum Movers
    'ORDI/USDT', 'TRB/USDT', 'BLUR/USDT', 'GAS/USDT', 'ARK/USDT', 
    'LOOM/USDT', 'BIGTIME/USDT', 'NOT/USDT', 'TON/USDT', 'IO/USDT', 
    'ATH/USDT', 'ZRO/USDT', 'LISTA/USDT', 'BB/USDT', 'OM/USDT', 
    'AERO/USDT', 'CELO/USDT', 'GMX/USDT', 'FIL/USDT', 'JTO/USDT',
    'PYTH/USDT', 'STRK/USDT', 'TNSR/USDT', 'DRIFT/USDT', 'ETHFI/USDT'
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

# ==========================================
# 4. MARKET ANALYSIS (5-Strategy & Breakout)
# ==========================================
def analyze_futures_market():
    exchange = ccxt.binance({
        'apiKey': BINANCE_API_KEY,
        'secret': BINANCE_SECRET_KEY,
        'enableRateLimit': True,
        'options': {'defaultType': 'future'}
    })
    
    for symbol in COINS_LIST:
        try:
            print(f"Scanning {symbol}...")
            bars = exchange.fetch_ohlcv(symbol, timeframe=TIMEFRAME, limit=200)
            df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
            
            # Indicators Calculation
            df['ema200'] = ta.ema(df['close'], length=200)
            df['rsi'] = ta.rsi(df['close'], length=14)
            macd = ta.macd(df['close'], fast=12, slow=26, signal=9)
            df['macd'] = macd['MACD_12_26_9']
            df['macd_signal'] = macd['MACDs_12_26_9']
            bb = ta.bbands(df['close'], length=20, std=2)
            df['bb_lower'] = bb['BBL_20_2.0']
            df['bb_upper'] = bb['BBU_20_2.0']
            df['vol_sma'] = ta.sma(df['volume'], length=20)

            # High / Low for Breakout Strategy (Last 20 Candles)
            df['high_20'] = df['high'].shift(1).rolling(20).max()
            df['low_20'] = df['low'].shift(1).rolling(20).min()

            # Latest Values
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

            # ------------------------------------
            # STRATEGY 1: ORIGINAL 5-STRATEGY SIGNALS
            # ------------------------------------
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
                sl = price * 0.985
                tp1 = price * 1.03
                tp2 = price * 1.05
                msg = (
                    f"🟢 *5-STRATEGY LONG SIGNAL*\n\n"
                    f"📌 *Coin:* `{symbol}`\n"
                    f"⚡ *Leverage:* {RECOMMENDED_LEVERAGE}\n"
                    f"📌 *Entry:* ${price:.4f}\n"
                    f"🛡️ *SL:* ${sl:.4f} (-1.5%)\n"
                    f"🎯 *TP1:* ${tp1:.4f} (+3.0%)\n"
                    f"🎯 *TP2:* ${tp2:.4f} (+5.0%)\n\n"
                    f"✅ 200 EMA + RSI Oversold + MACD + BB Support Match!"
                )
                send_telegram_msg(msg)

            # 5-Strategy SHORT
            elif is_downtrend and rsi_overbought and macd_bearish and near_bb_upper and good_volume:
                sl = price * 1.015
                tp1 = price * 0.97
                tp2 = price * 0.95
                msg = (
                    f"🔴 *5-STRATEGY SHORT SIGNAL*\n\n"
                    f"📌 *Coin:* `{symbol}`\n"
                    f"⚡ *Leverage:* {RECOMMENDED_LEVERAGE}\n"
                    f"📌 *Entry:* ${price:.4f}\n"
                    f"🛡️ *SL:* ${sl:.4f} (+1.5%)\n"
                    f"🎯 *TP1:* ${tp1:.4f} (-3.0%)\n"
                    f"🎯 *TP2:* ${tp2:.4f} (-5.0%)\n\n"
                    f"✅ 200 EMA + RSI Overbought + MACD + BB Resistance Match!"
                )
                send_telegram_msg(msg)

            # ------------------------------------
            # STRATEGY 2: BREAKOUT SIGNALS
            # ------------------------------------
            is_bullish_breakout = (price > high_20) and (prev_price <= high_20) and (price > ema200) and (volume > vol_sma * 1.5)
            is_bearish_breakout = (price < low_20) and (prev_price >= low_20) and (price < ema200) and (volume > vol_sma * 1.5)

            if is_bullish_breakout:
                sl = price * 0.98
                tp1 = price * 1.04
                tp2 = price * 1.08
                breakout_msg = (
                    f"🚀 *UPTREND BREAKOUT SIGNAL (BUY)*\n\n"
                    f"📌 *Coin:* `{symbol}`\n"
                    f"⚡ *Leverage:* {RECOMMENDED_LEVERAGE}\n"
                    f"📌 *Entry Price:* ${price:.4f}\n\n"
                    f"🛡️ *Stop Loss (SL):* ${sl:.4f} (-2.0%)\n"
                    f"🎯 *Take Profit 1:* ${tp1:.4f} (+4.0%)\n"
                    f"🎯 *Take Profit 2:* ${tp2:.4f} (+8.0%)\n\n"
                    f"🔥 *Breakout Confirmation:* \n"
                    f"✅ Broke 20-Period High Resistance (${high_20:.4f})\n"
                    f"✅ Strong Volume Surge (>1.5x Average)\n"
                    f"✅ Trading Above 200 EMA"
                )
                send_telegram_msg(breakout_msg)

            elif is_bearish_breakout:
                sl = price * 1.02
                tp1 = price * 0.96
                tp2 = price * 0.92
                breakout_msg = (
                    f"💥 *DOWNTREND BREAKOUT SIGNAL (SELL)*\n\n"
                    f"📌 *Coin:* `{symbol}`\n"
                    f"⚡ *Leverage:* {RECOMMENDED_LEVERAGE}\n"
                    f"📌 *Entry Price:* ${price:.4f}\n\n"
                    f"🛡️ *Stop Loss (SL):* ${sl:.4f} (+1.5%)\n"
                    f"🎯 *Take Profit 1:* ${tp1:.4f} (-4.0%)\n"
                    f"🎯 *Take Profit 2:* ${tp2:.4f} (-8.0%)\n\n"
                    f"🔥 *Breakout Confirmation:* \n"
                    f"✅ Broke 20-Period Low Support (${low_20:.4f})\n"
                    f"✅ Strong Volume Surge (>1.5x Average)\n"
                    f"✅ Trading Below 200 EMA"
                )
                send_telegram_msg(breakout_msg)

            time.sleep(1)

        except Exception as e:
            print(f"Error scanning {symbol}: {e}")

# ==========================================
# 5. MAIN EXECUTION LOOP
# ==========================================
if __name__ == "__main__":
    keep_alive()
    send_telegram_msg("🤖 *5-Strategy + Breakout Bot Started!* \nScanning 140+ futures pairs continuously...")
    print("Bot is running...")
    
    while True:
        try:
            print("\n--- Starting Scan (140+ Coins) ---")
            analyze_futures_market()
            print("--- Scan Complete. Waiting 5 minutes ---\n")
            time.sleep(300)
        except Exception as e:
            print(f"System Error: {e}")
            time.sleep(30)
