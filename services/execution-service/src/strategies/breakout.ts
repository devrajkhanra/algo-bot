import { Candle } from "../types/candle.js";

export type Signal = "BUY" | "SELL" | "NONE";

export const breakoutStrategy = (candles: Candle[]): Signal => {
  if (!candles || candles.length < 2) return "NONE";

  const prev = candles[candles.length - 2];
  const current = candles[candles.length - 1];

  if (!prev || !current) return "NONE";

  if (current.close > prev.high) {
    return "BUY";
  }

  if (current.close < prev.low) {
    return "SELL";
  }

  return "NONE";
};