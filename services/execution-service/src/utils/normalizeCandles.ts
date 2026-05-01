import { Candle } from "../types/candle.js";

export const normalizeCandles = (rawCandles: any[]): Candle[] => {
  return rawCandles.map((c) => ({
    time: new Date(
      new Date(c[0]).toLocaleString("en-US", {
        timeZone: "Asia/Kolkata",
      })
    ),
    open: Number(c[1]),
    high: Number(c[2]),
    low: Number(c[3]),
    close: Number(c[4]),
    volume: Number(c[5]),
  }));
};