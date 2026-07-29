import ccxt
import pandas as pd
import requests
import time

# ==========================================
# 1. TELEGRAM & API CREDENTIALS
# ==========================================
TELEGRAM_BOT_TOKEN = '8977777997:AAEvwcbsgOK0Gafij9rMx87_lQMeFUsI0C4'
TELEGRAM_CHAT_ID = '1371553688'

BINANCE_API_KEY = 'ZkGqBNIEcLPKboCW9xy1R4sUW2QZ9IYzGAV1TuGn6d2DInEBR7iEBNDU1Z9Kjmuw'
BINANCE_SECRET_KEY = '4Pwys4qWhublkEPUmoDKmF5Tfh818ji1SR4wjuWnVh1SEGION4824tqZjuSR4Ep3'  # உங்களின் Secret Key-ஐ இங்கு போடவும்

# ==========================================
# 2. FULL 150 FUTURES COINS LIST
# ==========================================
COINS_LIST = [
    'BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'XRP/USDT',
    'ADA/USDT', 'DOGE/USDT', 'AVAX/USDT', 'LINK/USDT', 'SUI/USDT',
    'DOT/USDT', 'POL/USDT', 'LTC/USDT', 'BCH/USDT', 'NEAR/USDT',
    'APT/USDT', 'ARB/USDT', 'OP/USDT', 'INJ/USDT', 'TIA/USDT',
    'ON/USDT', 'BTW/USDT', 'UB/USDT', 'BEAT/USDT', 'EUL/USDT', 
    'SOXS/USDT', 'BOT/USDT', 'ZIL/USDT', 'HOLO/USDT', 'HK1810/USDT', 
    'FLOW/USDT', 'ZEST/USDT', 'SOON/USDT', 'IRYS/USDT', 'TAKE/USDT', 
    'PROM/USDT', 'POPMART/USDT', 'PHAROS/USDT', 'SLX/USDT', 'TER/USDT', 
    'LIT/USDT', '1000CHEEMS/USDT', 'OPEN/USDT', 'IBM/USDT', 'NOW/USDT', 
    'ADBE/USDT', 'GPS/USDT', 'KOMA/USDT', 'TURTLE/USDT', 'CRM/USDT', 
    'SONY/USDT', 'KMNO/USDT', 'TUT/USDT', 'RENDER/USDT', 'FET/USDT', 
    'TAO/USDT', 'WLD/USDT', 'ARKM/USDT', 'AGIX/USDT', 'OCEAN/USDT', 
    'AKT/USDT', 'NMR/USDT', 'GRT/USDT', '1000PEPE/USDT', '1000SHIB/USDT', 
    '1000FLOKI/USDT', 'WIF/USDT', '1000BONK/USDT', '1000SATS/USDT', 'MEME/USDT', 
    'PEOPLE/USDT', 'MYRO/USDT', 'POPCAT/USDT', 'BRETT/USDT', 'MEW/USDT', 
    'TURBO/USDT', 'NEIRO/USDT', 'BOME/USDT', 'SEI/USDT', 'STX/USDT', 
    'ATOM/USDT', 'FTM/USDT', 'ALGO/USDT', 'EGLD/USDT', 'KAS/USDT', 
    'ROSE/USDT', 'STRK/USDT', 'MANTA/USDT', 'ALT/USDT', 'METIS/USDT', 
    'ZK/USDT', 'BLAST/USDT', 'RON/USDT', 'ZETA/USDT', 'SGLD/USDT', 
    'DYM/USDT', 'PYTH/USDT', 'TNSR/USDT', 'UNI/USDT', 'AAVE/USDT', 
    'MKR/USDT', 'CRV/USDT', 'LDO/USDT', 'PENDLE/USDT', 'JUP/USDT', 
    'RUNE/USDT', 'ENA/USDT', 'SNX/USDT', 'COMP/USDT', 'DYDX/USDT', 
    '1INCH/USDT', 'CAKE/USDT', 'RAY/USDT', 'CVX/USDT', 'SUSHI/USDT', 
    'KAVA/USDT', 'FXS/USDT', 'GMX/USDT', 'GALA/USDT', 'SAND/USDT', 
    'MANA/USDT', 'IMX/USDT', 'BEAM/USDT', 'PIXEL/USDT', 'YGG/USDT', 
    'AXS/USDT', 'ILV/USDT', 'ALICE/USDT', 'ENJ/USDT', 'MAGIC/USDT', 
    'HERO/USDT', 'TLM/USDT', 'DAR/USDT', 'ORDI/USDT', 'TRB/USDT', 
    'BLUR/USDT', 'GAS/USDT', 'ARK/USDT', 'LOOM/USDT', 'BIGTIME/USDT', 
    'NOT/USDT', 'TON/USDT', 'IO/USDT', 'ATH/USDT', 'ZRO/USDT', 
    'LISTA/USDT', 'BB/USDT', 'OM/USDT', 'AERO/USDT', 'CELO/USDT', 
    'FIL/USDT', 'JTO/USDT', 'DRIFT/USDT', 'ETHFI/USDT', 'ZEN/USDT', 
    'SSV/USDT', 'RNDR/USDT', 'SUPER/USDT'
]

TIMEFRAME_PRIMARY = '1h'
TIMEFRAME_CONFIRM = '4h'
RECOMMENDED_LEVERAGE = "3x - 5x (Isolated)"

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

def calculate_indicators(df):
    # EMA 200
    df['ema200'] = df['close'].ewm(span=200, adjust=False).mean()
    
    # RSI (14)
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))

    # MACD
    exp1 = df['close'].ewm(span=12, adjust=False).mean()
    exp2 = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = exp1 - exp2
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()

    # Bollinger Bands
    sma = df['close'].rolling(window=20).mean()
    std = df['close'].rolling(window=20).std()
    df['bb_upper'] = sma + (std * 2)
    df['bb_lower'] = sma - (std * 2)

    # Volume & High/Low 20
    df['vol_sma'] = df['volume'].rolling(window=20).mean()
    df['high_20'] = df['high'].shift(1).rolling(20).max()
    df['low_20'] = df['low'].shift(1).rolling(20).min()

    # ATR (Average True Range) for Dynamic SL/TP
    high_low = df['high'] - df['low']
    high_cp = (df['high'] - df['close'].shift(1)).abs()
    low_cp = (df['low'] - df['close'].shift(1)).abs()
    tr = pd.concat([high_low, high_cp, low_cp], axis=1).max(axis=1)
    df['atr'] = tr.rolling(14).mean()

    return df

def get_btc_trend(exchange):
    """Bitcoin சந்தை அப்-ட்ரெண்டா அல்லது டவுன்-ட்ரெண்டா எனக் கண்டறிதல்"""
    try:
        bars = exchange.fetch_ohlcv('BTC/USDT', timeframe=TIMEFRAME_CONFIRM, limit=200)
        df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
        df['ema200'] = df['close'].ewm(span=200, adjust=False).mean()
        price = df['close'].iloc[-1]
        ema200 = df['ema200'].iloc[-1]
        return "BULLISH" if price > ema200 else "BEARISH"
    except Exception as e:
        print(f"Error fetching BTC trend: {e}")
        return "NEUTRAL"

def analyze_futures_market():
    exchange = ccxt.binance({
        'apiKey': BINANCE_API_KEY,
        'secret': BINANCE_SECRET_KEY,
        'enableRateLimit': True,
        'options': {'defaultType': 'future'}
    })

    btc_trend = get_btc_trend(exchange)
    print(f"Current BTC Trend (4h): {btc_trend}")
    
    for symbol in COINS_LIST:
        try:
            # Fetch 1h Primary Data
            bars_1h = exchange.fetch_ohlcv(symbol, timeframe=TIMEFRAME_PRIMARY, limit=200)
            df_1h = pd.DataFrame(bars_1h, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
            df_1h = calculate_indicators(df_1h)

            # Fetch 4h Higher Timeframe Data
            bars_4h = exchange.fetch_ohlcv(symbol, timeframe=TIMEFRAME_CONFIRM, limit=200)
            df_4h = pd.DataFrame(bars_4h, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
            df_4h['ema200'] = df_4h['close'].ewm(span=200, adjust=False).mean()

            price = df_1h['close'].iloc[-1]
            prev_price = df_1h['close'].iloc[-2]
            ema200 = df_1h['ema200'].iloc[-1]
            rsi = df_1h['rsi'].iloc[-1]
            macd_val = df_1h['macd'].iloc[-1]
            macd_sig = df_1h['macd_signal'].iloc[-1]
            bb_lower = df_1h['bb_lower'].iloc[-1]
            bb_upper = df_1h['bb_upper'].iloc[-1]
            volume = df_1h['volume'].iloc[-1]
            vol_sma = df_1h['vol_sma'].iloc[-1]
            high_20 = df_1h['high_20'].iloc[-1]
            low_20 = df_1h['low_20'].iloc[-1]
            atr = df_1h['atr'].iloc[-1]

            # 4h Trend Check
            tf4h_uptrend = price > df_4h['ema200'].iloc[-1]
            tf4h_downtrend = price < df_4h['ema200'].iloc[-1]

            # Conditions
            is_uptrend = (price > ema200) and tf4h_uptrend and (btc_trend == "BULLISH")
            is_downtrend = (price < ema200) and tf4h_downtrend and (btc_trend == "BEARISH")
            
            rsi_oversold = rsi < 42
            rsi_overbought = rsi > 58
            macd_bullish = macd_val > macd_sig
            macd_bearish = macd_val < macd_sig
            near_bb_lower = price <= (bb_lower * 1.008)
            near_bb_upper = price >= (bb_upper * 0.992)
            good_volume = volume > (vol_sma * 1.2)

            # Dynamic ATR Stop Loss & Take Profit
            long_sl = price - (atr * 1.5)
            long_tp1 = price + (atr * 2.0)
            long_tp2 = price + (atr * 3.5)

            short_sl = price + (atr * 1.5)
            short_tp1 = price - (atr * 2.0)
            short_tp2 = price - (atr * 3.5)

            # 1. HIGH-ACCURACY LONG SIGNAL
            if is_uptrend and rsi_oversold and macd_bullish and near_bb_lower and good_volume:
                send_telegram_msg(
                    f"🎯 *HIGH-ACCURACY LONG SIGNAL*\n\n"
                    f"📌 *Coin:* `{symbol}`\n"
                    f"⚡ *Leverage:* {RECOMMENDED_LEVERAGE}\n"
                    f"📌 *Entry:* ${price:.4f}\n"
                    f"🛡️ *Dynamic SL (ATR):* ${long_sl:.4f}\n"
                    f"🎯 *TP1:* ${long_tp1:.4f}\n"
                    f"🎯 *TP2:* ${long_tp2:.4f}\n\n"
                    f"🔍 *Filters Passed:* BTC Bullish | 4h Uptrend | High Volume"
                )

            # 2. HIGH-ACCURACY SHORT SIGNAL
            elif is_downtrend and rsi_overbought and macd_bearish and near_bb_upper and good_volume:
                send_telegram_msg(
                    f"🎯 *HIGH-ACCURACY SHORT SIGNAL*\n\n"
                    f"📌 *Coin:* `{symbol}`\n"
                    f"⚡ *Leverage:* {RECOMMENDED_LEVERAGE}\n"
                    f"📌 *Entry:* ${price:.4f}\n"
                    f"🛡️ *Dynamic SL (ATR):* ${short_sl:.4f}\n"
                    f"🎯 *TP1:* ${short_tp1:.4f}\n"
                    f"🎯 *TP2:* ${short_tp2:.4f}\n\n"
                    f"🔍 *Filters Passed:* BTC Bearish | 4h Downtrend | High Volume"
                )

            # 3. BREAKOUT SIGNALS
            is_bullish_breakout = (price > high_20) and (prev_price <= high_20) and is_uptrend and (volume > vol_sma * 1.8)
            is_bearish_breakout = (price < low_20) and (prev_price >= low_20) and is_downtrend and (volume > vol_sma * 1.8)

            if is_bullish_breakout:
                send_telegram_msg(
                    f"🚀 *STRONG UPTREND BREAKOUT*\n\n"
                    f"📌 *Coin:* `{symbol}`\n"
                    f"📌 *Entry:* ${price:.4f}\n"
                    f"🛡️ *SL:* ${long_sl:.4f}\n"
                    f"🎯 *TP1:* ${long_tp1:.4f}\n"
                    f"🎯 *TP2:* ${long_tp2:.4f}"
                )

            elif is_bearish_breakout:
                send_telegram_msg(
                    f"💥 *STRONG DOWNTREND BREAKOUT*\n\n"
                    f"📌 *Coin:* `{symbol}`\n"
                    f"📌 *Entry:* ${price:.4f}\n"
                    f"🛡️ *SL:* ${short_sl:.4f}\n"
                    f"🎯 *TP1:* ${short_tp1:.4f}\n"
                    f"🎯 *TP2:* ${short_tp2:.4f}"
                )

            time.sleep(0.3)
        except Exception as e:
            print(f"Error {symbol}: {e}")

if __name__ == "__main__":
    send_telegram_msg("hi mano signal anazlyzed")
    analyze_futures_market()
