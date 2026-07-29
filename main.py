import ccxt
import pandas as pd
import pandas_ta as ta
import requests
import time
from flask import Flask
from threading import Thread

# ==========================================
# 1. KEEP-ALIVE WEB SERVER (For 24/7 Hosting)
# ==========================================
app = Flask('')

@app.route('/')
def home():
    return "Crypto Futures Bot is Running 24/7!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# ==========================================
# 2. API & TELEGRAM CREDENTIALS
# ==========================================
TELEGRAM_BOT_TOKEN = '8977777997:AAEvwcbsgOK0Gafij9rMx87_lQMeFUsI0C4'
TELEGRAM_CHAT_ID = '1371553688'

BINANCE_API_KEY = 'linLKfb5vlCVsrSwhY3GgUA9yR3jX8BeQlL5UqI3xDZeLqxo08wAx4st2aiVvrkS'
BINANCE_SECRET_KEY = '4Pwys4qWhublkEPUmoDKmF5Tfh818ji1SR4wjuWnVh1SEGION4824tqZjuSR4Ep3'  # உங்களின் Secret Key-ஐ இங்கு போடவும்

# ==========================================
# 3. TOP 50 FUTURES COINS LIST
# ==========================================
COINS_LIST = [
    'BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'XRP/USDT',
    'ADA/USDT', 'DOGE/USDT', 'AVAX/USDT', 'LINK/USDT', 'SUI/USDT',
    'DOT/USDT', 'MATIC/USDT', 'LTC/USDT', 'BCH/USDT', 'NEAR/USDT',
    'APT/USDT', 'ARB/USDT', 'OP/USDT', 'INJ/USDT', 'TIA/USDT',
    'RNDR/USDT', 'FET/USDT', 'SEI/USDT', 'STX/USDT', 'ATOM/USDT',
    'UNI/USDT', 'AAVE/USDT', 'MKR/USDT', 'CRV/USDT', 'LDO/USDT',
    'GRT/USDT', 'FIL/USDT', 'THETA/USDT', 'ICP/USDT', 'EGLD/USDT',
    'PEPE/USDT', 'SHIB/USDT', 'FLOKI/USDT', 'WIF/USDT', 'BONK/USDT',
    'GALA/USDT', 'SAND/USDT', 'MANA/USDT', 'IMX/USDT', 'GMX/USDT',
    'PENDLE/USDT', 'JUP/USDT', 'ORDI/USDT', 'KAS/USDT', 'RUNE/USDT'
]

TIMEFRAME = '1h'
RECOMMENDED_LEVERAGE = "3x - 5x (Isolated)"

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

# ==========================================
# 4. 5-STRATEGY MARKET ANALYSIS
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
            print(f"Scanning 5 Strategies for {symbol}...")
            bars = exchange.fetch_ohlcv(symbol, timeframe=TIMEFRAME, limit=200)
            df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
            
            # --- CALCULATING 5 INDICATORS ---
            # 1. Trend: 200 EMA
            df['ema200'] = ta.ema(df['close'], length=200)
            
            # 2. Momentum: RSI (14)
            df['rsi'] = ta.rsi(df['close'], length=14)
            
            # 3. Trend & Momentum: MACD (12, 26, 9)
            macd = ta.macd(df['close'], fast=12, slow=26, signal=9)
            df['macd'] = macd['MACD_12_26_9']
            df['macd_signal'] = macd['MACDs_12_26_9']
            
            # 4. Volatility: Bollinger Bands (20, 2)
            bb = ta.bbands(df['close'], length=20, std=2)
            df['bb_lower'] = bb['BBL_20_2.0']
            df['bb_upper'] = bb['BBU_20_2.0']
            
            # 5. Volume Confirmation: Volume SMA (20)
            df['vol_sma'] = ta.sma(df['volume'], length=20)

            # Latest Values
            price = df['close'].iloc[-1]
            ema200 = df['ema200'].iloc[-1]
            rsi = df['rsi'].iloc[-1]
            macd_val = df['macd'].iloc[-1]
            macd_sig = df['macd_signal'].iloc[-1]
            bb_lower = df['bb_lower'].iloc[-1]
            bb_upper = df['bb_upper'].iloc[-1]
            volume = df['volume'].iloc[-1]
            vol_sma = df['vol_sma'].iloc[-1]

            # --- STRATEGY CONDITIONS ---
            # 1. Trend Condition
            is_uptrend = price > ema200
            is_downtrend = price < ema200

            # 2. RSI Condition
            rsi_oversold = rsi < 42
            rsi_overbought = rsi > 58

            # 3. MACD Condition
            macd_bullish = macd_val > macd_sig
            macd_bearish = macd_val < macd_sig

            # 4. Bollinger Bands Condition
            near_bb_lower = price <= (bb_lower * 1.008)  # Lower Band-க்கு அருகில்
            near_bb_upper = price >= (bb_upper * 0.992)  # Upper Band-க்கு அருகில்

            # 5. Volume Condition
            good_volume = volume > (vol_sma * 0.8)

            # 🟢 MULTI-STRATEGY LONG SIGNAL
            if is_uptrend and rsi_oversold and macd_bullish and near_bb_lower and good_volume:
                sl = price * 0.985      # 1.5% Stop Loss
                tp1 = price * 1.03      # 3.0% Take Profit 1
                tp2 = price * 1.05      # 5.0% Take Profit 2

                signal_msg = (
                    f"🟢 *HIGH PROBABILITY LONG SIGNAL (BUY)*\n\n"
                    f"📌 *Coin:* `{symbol}`\n"
                    f"⚡ *Suggested Leverage:* {RECOMMENDED_LEVERAGE}\n"
                    f"📌 *Entry Price:* ${price:.4f}\n\n"
                    f"🛡️ *Stop Loss (SL):* ${sl:.4f} (-1.5%)\n"
                    f"🎯 *Take Profit 1:* ${tp1:.4f} (+3.0%)\n"
                    f"🎯 *Take Profit 2:* ${tp2:.4f} (+5.0%)\n\n"
                    f"📊 *5 Strategies Match:* \n"
                    f"✅ Above 200 EMA (Uptrend)\n"
                    f"✅ RSI Oversold ({rsi:.1f})\n"
                    f"✅ MACD Bullish Crossover\n"
                    f"✅ Touched Lower Bollinger Band\n"
                    f"✅ Volume Confirmed"
                )
                send_telegram_msg(signal_msg)
                print(f"✅ Multi-Strategy LONG Signal sent for {symbol}!")

            # 🔴 MULTI-STRATEGY SHORT SIGNAL
            elif is_downtrend and rsi_overbought and macd_bearish and near_bb_upper and good_volume:
                sl = price * 1.015      # 1.5% Stop Loss
                tp1 = price * 0.97      # 3.0% Take Profit 1
                tp2 = price * 0.95      # 5.0% Take Profit 2

                signal_msg = (
                    f"🔴 *HIGH PROBABILITY SHORT SIGNAL (SELL)*\n\n"
                    f"📌 *Coin:* `{symbol}`\n"
                    f"⚡ *Suggested Leverage:* {RECOMMENDED_LEVERAGE}\n"
                    f"📌 *Entry Price:* ${price:.4f}\n\n"
                    f"🛡️ *Stop Loss (SL):* ${sl:.4f} (+1.5%)\n"
                    f"🎯 *Take Profit 1:* ${tp1:.4f} (-3.0%)\n"
                    f"🎯 *Take Profit 2:* ${tp2:.4f} (-5.0%)\n\n"
                    f"📊 *5 Strategies Match:* \n"
                    f"✅ Below 200 EMA (Downtrend)\n"
                    f"✅ RSI Overbought ({rsi:.1f})\n"
                    f"✅ MACD Bearish Crossover\n"
                    f"✅ Touched Upper Bollinger Band\n"
                    f"✅ Volume Confirmed"
                )
                send_telegram_msg(signal_msg)
                print(f"✅ Multi-Strategy SHORT Signal sent for {symbol}!")

            time.sleep(1.5)  # API Rate limits தவிர்க்க சிறிய இடைவெளி

        except Exception as e:
            print(f"Error scanning {symbol}: {e}")

# ==========================================
# 5. MAIN EXECUTION LOOP
# ==========================================
if __name__ == "__main__":
    keep_alive()  # Web server for 24/7 execution
    
    send_telegram_msg("🤖 *5-Strategy Crypto Futures Bot Started!* \nScanning Top 50 Coins continuously...")
    print("Bot is running...")
    
    while True:
        try:
            print("\n--- Starting Scan for 50 Coins ---")
            analyze_futures_market()
            print("--- Scan Complete. Waiting 5 minutes ---\n")
            time.sleep(300)  # 5 நிமிடங்களுக்கு ஒருமுறை அனலைஸ் செய்யும்
        except Exception as e:
            print(f"System Error: {e}")
            time.sleep(30)
