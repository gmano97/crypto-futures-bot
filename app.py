import ccxt
import pandas as pd
import pandas_ta as ta
import requests
import time
import os
import math
from datetime import datetime, timedelta
from flask import Flask
from threading import Thread, Lock

# ==========================================
# 1. KEEP-ALIVE WEB SERVER FOR RENDER
# ==========================================
app = Flask('')

@app.route('/')
def home():
    return "Crypto Futures Bot v4.1 (OKX | VIP & TP3) is Active & Running 24/7!"

@app.route('/health')
def health():
    return {"status": "ok", "bot": "Crypto Futures Bot v4.1 OKX"}

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# ==========================================
# 2. TELEGRAM CREDENTIALS
# ==========================================
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID   = os.environ.get("TELEGRAM_CHAT_ID")

def check_credentials():
    missing = [k for k, v in {
        "TELEGRAM_BOT_TOKEN": TELEGRAM_BOT_TOKEN,
        "TELEGRAM_CHAT_ID":   TELEGRAM_CHAT_ID,
    }.items() if not v]
    if missing:
        print(f"❌ Missing required secrets: {', '.join(missing)}")
        return False
    return True

# ==========================================
# 3. SIGNAL COOLDOWN
# ==========================================
SIGNAL_COOLDOWN_HOURS = 2
signal_last_sent: dict[tuple, datetime] = {}

def is_on_cooldown(symbol: str, direction: str) -> bool:
    key = (symbol, direction)
    last = signal_last_sent.get(key)
    if last is None:
        return False
    return datetime.utcnow() - last < timedelta(hours=SIGNAL_COOLDOWN_HOURS)

def mark_signal_sent(symbol: str, direction: str):
    signal_last_sent[(symbol, direction)] = datetime.utcnow()

# ==========================================
# 4. OPEN TRADE TRACKER
# ==========================================
open_trades: dict[str, dict] = {}
trades_lock = Lock()
MAX_TRADE_AGE_HOURS = 24

def trade_key(symbol: str, direction: str) -> str:
    return f"{symbol}_{direction}"

def add_open_trade(symbol, direction, entry, sl, tp1, tp2, tp3, signal_type):
    key = trade_key(symbol, direction)
    with trades_lock:
        open_trades[key] = {
            "symbol":      symbol,
            "direction":   direction,
            "entry":       entry,
            "sl":          sl,
            "tp1":         tp1,
            "tp2":         tp2,
            "tp3":         tp3,
            "tp1_hit":     False,
            "tp2_hit":     False,
            "signal_type": signal_type,
            "opened_at":   datetime.utcnow(),
        }
    print(f"  📂 Tracking: {symbol} {direction} | SL={sl:.4f} TP3={tp3:.4f}")

# ==========================================
# 5. TELEGRAM HELPER
# ==========================================
def send_telegram_msg(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

# ==========================================
# 6. TP/SL MONITOR THREAD
# ==========================================
def monitor_open_trades():
    monitor_exchange = ccxt.okx({
        'enableRateLimit': True,
        'options': {'defaultType': 'swap'},
    })
    print("🔍 TP/SL monitor thread started (OKX | TP3 tracking)")

    while True:
        try:
            time.sleep(60)
            with trades_lock:
                symbols_to_check = list(open_trades.items())

            if not symbols_to_check:
                continue

            for key, trade in symbols_to_check:
                try:
                    symbol    = trade["symbol"]
                    direction = trade["direction"]
                    entry     = trade["entry"]
                    sl        = trade["sl"]
                    tp1       = trade["tp1"]
                    tp2       = trade["tp2"]
                    tp3       = trade["tp3"]
                    tp1_hit   = trade["tp1_hit"]
                    tp2_hit   = trade["tp2_hit"]
                    sig_type  = trade["signal_type"]
                    opened_at = trade["opened_at"]

                    if datetime.utcnow() - opened_at > timedelta(hours=MAX_TRADE_AGE_HOURS):
                        with trades_lock:
                            open_trades.pop(key, None)
                        send_telegram_msg(
                            f"⏰ *TRADE EXPIRED (24h)*\n\n"
                            f"🪙 *Asset:* `{symbol}`\n"
                            f"📊 *Signal:* {sig_type}\n"
                            f"📌 *Entry:* ${entry:.4f}\n"
                            f"Targets not reached within 24 hours. Trade removed."
                        )
                        continue

                    ticker = monitor_exchange.fetch_ticker(symbol)
                    price  = ticker['last']

                    if direction == "LONG":
                        if price <= sl:
                            pct = ((price - entry) / entry) * 100
                            send_telegram_msg(f"🔴 *STOP LOSS HIT*\n\n🪙 `{symbol}`\n💔 SL: ${price:.4f} ({pct:.2f}%)")
                            with trades_lock: open_trades.pop(key, None)
                        elif price >= tp3:
                            pct = ((price - entry) / entry) * 100
                            send_telegram_msg(f"🚀 *TP3 HIT — ULTIMATE TARGET!* 🏆\n\n🪙 `{symbol}`\n🎯 TP3: ${price:.4f} (+{pct:.2f}%)")
                            with trades_lock: open_trades.pop(key, None)
                        elif price >= tp2 and not tp2_hit:
                            pct = ((price - entry) / entry) * 100
                            send_telegram_msg(f"🎯 *TP2 HIT!*\n\n🪙 `{symbol}`\n✅ TP2: ${price:.4f} (+{pct:.2f}%)")
                            with trades_lock:
                                if key in open_trades: open_trades[key]["tp2_hit"] = True
                        elif price >= tp1 and not tp1_hit:
                            pct = ((price - entry) / entry) * 100
                            send_telegram_msg(f"🎯 *TP1 HIT!*\n\n🪙 `{symbol}`\n✅ TP1: ${price:.4f} (+{pct:.2f}%)\n💡 Move SL to entry.")
                            with trades_lock:
                                if key in open_trades: open_trades[key]["tp1_hit"] = True

                    elif direction == "SHORT":
                        if price >= sl:
                            pct = ((entry - price) / entry) * 100
                            send_telegram_msg(f"🔴 *STOP LOSS HIT*\n\n🪙 `{symbol}`\n💔 SL: ${price:.4f}")
                            with trades_lock: open_trades.pop(key, None)
                        elif price <= tp3:
                            pct = ((entry - price) / entry) * 100
                            send_telegram_msg(f"🚀 *TP3 HIT — ULTIMATE TARGET!* 🏆\n\n🪙 `{symbol}`\n🎯 TP3: ${price:.4f}")
                            with trades_lock: open_trades.pop(key, None)
                        elif price <= tp2 and not tp2_hit:
                            pct = ((entry - price) / entry) * 100
                            send_telegram_msg(f"🎯 *TP2 HIT!*\n\n🪙 `{symbol}`\n✅ TP2: ${price:.4f}")
                            with trades_lock:
                                if key in open_trades: open_trades[key]["tp2_hit"] = True
                        elif price <= tp1 and not tp1_hit:
                            pct = ((entry - price) / entry) * 100
                            send_telegram_msg(f"🎯 *TP1 HIT!*\n\n🪙 `{symbol}`\n✅ TP1: ${price:.4f}\n💡 Move SL to entry.")
                            with trades_lock:
                                if key in open_trades: open_trades[key]["tp1_hit"] = True

                    time.sleep(0.3)
                except Exception as e:
                    print(f"Monitor error: {e}")
        except Exception as e:
            print(f"Monitor thread error: {e}")
            time.sleep(30)

def start_monitor_thread():
    t = Thread(target=monitor_open_trades)
    t.daemon = True
    t.start()

# ==========================================
# 7. HEARTBEAT THREAD
# ==========================================
HEARTBEAT_INTERVAL_MIN = 20

def heartbeat_loop():
    time.sleep(HEARTBEAT_INTERVAL_MIN * 60)
    while True:
        try:
            now = datetime.utcnow().strftime('%H:%M UTC')
            with trades_lock:
                active = len(open_trades)
            send_telegram_msg(f"🟢 *Bot Active* | `{now}`\n📂 Monitoring {active} open trade(s).")
        except Exception as e:
            print(f"Heartbeat error: {e}")
        time.sleep(HEARTBEAT_INTERVAL_MIN * 60)

def start_heartbeat_thread():
    t = Thread(target=heartbeat_loop)
    t.daemon = True
    t.start()

# ==========================================
# 8. MARKET SCANNER
# ==========================================
def get_all_futures_symbols(exchange) -> list[str]:
    try:
        markets = exchange.load_markets()
    except Exception as e:
        return []
    return [s for s, m in markets.items() if m.get('active') and m.get('settle') == 'USDT' and m.get('type') == 'swap' and m.get('linear')]

TIMEFRAME = '1h'
RECOMMENDED_LEVERAGE = "3x - 5x (Isolated)"
ADX_THRESHOLD = 28
MIN_VOLUME_USDT = 8_000_000

def analyze_futures_market():
    exchange = ccxt.okx({'enableRateLimit': True, 'options': {'defaultType': 'swap'}})
    coins_list = get_all_futures_symbols(exchange)
    if not coins_list: return

    signals_sent = 0
    for symbol in coins_list:
        try:
            bars = exchange.fetch_ohlcv(symbol, timeframe=TIMEFRAME, limit=220)
            if len(bars) < 200: continue
            df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'volume'])

            if (df['volume'].iloc[-24:] * df['close'].iloc[-24:]).sum() < MIN_VOLUME_USDT: continue

            df['ema200'] = ta.ema(df['close'], length=200)
            df['rsi']    = ta.rsi(df['close'], length=14)
            macd = ta.macd(df['close'], fast=12, slow=26, signal=9)
            if macd is None or macd.empty: continue
            df['macd'], df['macd_signal'] = macd['MACD_12_26_9'], macd['MACDs_12_26_9']

            bb = ta.bbands(df['close'], length=20, std=2)
            if bb is None or bb.empty: continue
            bbl_col = next(c for c in bb.columns if c.startswith('BBL'))
            bbu_col = next(c for c in bb.columns if c.startswith('BBU'))
            df['bb_lower'], df['bb_upper'] = bb[bbl_col], bb[bbu_col]

            df['vol_sma'] = ta.sma(df['volume'], length=20)
            adx_df = ta.adx(df['high'], df['low'], df['close'], length=14)
            if adx_df is None or adx_df.empty: continue
            adx_col = next(c for c in adx_df.columns if c.startswith('ADX'))
            df['adx'] = adx_df[adx_col]

            price, ema200, rsi = df['close'].iloc[-1], df['ema200'].iloc[-1], df['rsi'].iloc[-1]
            macd_val, macd_sig = df['macd'].iloc[-1], df['macd_signal'].iloc[-1]
            bb_lower, bb_upper = df['bb_lower'].iloc[-1], df['bb_upper'].iloc[-1]
            volume, vol_sma, adx = df['volume'].iloc[-1], df['vol_sma'].iloc[-1], df['adx'].iloc[-1]

            if any(math.isnan(v) for v in [ema200, rsi, macd_val, macd_sig, bb_lower, bb_upper, vol_sma, adx]): continue
            if adx < ADX_THRESHOLD: continue

            if price > ema200 and rsi < 42 and macd_val > macd_sig and price <= (bb_lower * 1.008) and volume > (vol_sma * 0.8):
                if not is_on_cooldown(symbol, "LONG"):
                    sl, tp1, tp2, tp3 = price * 0.981, price * 1.025, price * 1.050, price * 1.085
                    msg = f"🟢 *VIP LONG • {symbol}*\n\n⚡ Lev: {RECOMMENDED_LEVERAGE}\n📍 Entry: `${price:.4f}`\n🛡️ SL: `${sl:.4f}`\n🎯 TP1: `${tp1:.4f}`\n🎯 TP2: `${tp2:.4f}`\n🚀 TP3: `${tp3:.4f}`"
                    send_telegram_msg(msg)
                    mark_signal_sent(symbol, "LONG")
                    add_open_trade(symbol, "LONG", price, sl, tp1, tp2, tp3, "5-STRATEGY LONG")
                    signals_sent += 1

            elif price < ema200 and rsi > 58 and macd_val < macd_sig and price >= (bb_upper * 0.992) and volume > (vol_sma * 0.8):
                if not is_on_cooldown(symbol, "SHORT"):
                    sl, tp1, tp2, tp3 = price * 1.019, price * 0.975, price * 0.950, price * 0.915
                    msg = f"🔴 *VIP SHORT • {symbol}*\n\n⚡ Lev: {RECOMMENDED_LEVERAGE}\n📍 Entry: `${price:.4f}`\n🛡️ SL: `${sl:.4f}`\n🎯 TP1: `${tp1:.4f}`\n🎯 TP2: `${tp2:.4f}`\n🚀 TP3: `${tp3:.4f}`"
                    send_telegram_msg(msg)
                    mark_signal_sent(symbol, "SHORT")
                    add_open_trade(symbol, "SHORT", price, sl, tp1, tp2, tp3, "5-STRATEGY SHORT")
                    signals_sent += 1
            time.sleep(0.5)
        except Exception as e:
            print(f"Error scanning {symbol}: {e}")

# ==========================================
# 9. MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    if not check_credentials():
        exit(1)

    keep_alive()
    start_monitor_thread()
    start_heartbeat_thread()

    send_telegram_msg("🤖 *Crypto Futures Bot v4.1 Started on Render! (OKX)*")
    print("Bot v4.1 is running...")

    while True:
        try:
            analyze_futures_market()
            time.sleep(300)
        except Exception as e:
            print(f"System Error: {e}")
            time.sleep(30)
