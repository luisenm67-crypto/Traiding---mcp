
import os
import yfinance as yf
import ta
from mcp.server.fastmcp import FastMCP

puerto = int(os.environ.get("PORT", 8000))
mcp = FastMCP("MultiAssetTrading", host="0.0.0.0", port=puerto)

def normalizar_ticker(simbolo: str, mercado: str) -> str:
    s = simbolo.upper().strip()
    m = mercado.lower().strip()
    if m == "cripto" and "-" not in s:
        return f"{s}-USD"
    elif m == "forex" and not s.endswith("=X"):
        return f"{s}=X"
    elif m == "futuros" and not s.endswith("=F"):
        return f"{s}=F"
    return s

@mcp.tool()
def analizar_activo(
    simbolo: str,
    mercado: str = "acciones",
    periodo: str = "3mo",
    intervalo: str = "1d"
) -> str:
    """
    Obtiene velas OHLCV e indicadores técnicos (RSI, EMA20, EMA50, ATR).
    - mercado: 'cripto', 'acciones', 'forex', o 'futuros'
    - simbolo: ej. 'BTC', 'AAPL', 'EURUSD', 'NQ', 'GC'
    - intervalo: '15m', '1h', '1d', '1wk'
    """
    ticker_yf = normalizar_ticker(simbolo, mercado)
    df = yf.Ticker(ticker_yf).history(period=periodo, interval=intervalo)

    if df.empty:
        return f"No se encontraron datos para {ticker_yf}."

    df["RSI_14"] = ta.momentum.rsi(df["Close"], window=14).round(2)
    df["EMA_20"] = ta.trend.ema_indicator(df["Close"], window=20).round(4)
    df["EMA_50"] = ta.trend.ema_indicator(df["Close"], window=50).round(4)
    df["ATR_14"] = ta.volatility.average_true_range(
        df["High"], df["Low"], df["Close"], window=14
    ).round(4)

    columnas = ["Open", "High", "Low", "Close", "Volume", "RSI_14", "EMA_20", "EMA_50", "ATR_14"]
    return f"Activo: {ticker_yf} ({intervalo})\n" + df[columnas].tail(40).to_csv()

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
