import express from "express";
import { getAccessToken } from "./auth/token.js";
import { getCandleData } from "./api/marketData.js";
import { Candle } from "./types/candle.js";

export const normalizeCandles = (rawCandles: any[]): Candle[] => {
    return rawCandles.map((c) => ({
        time: new Date(c[0]),
        open: Number(c[1]),
        high: Number(c[2]),
        low: Number(c[3]),
        close: Number(c[4]),
        volume: Number(c[5]),
    }));
};

const app = express();
const PORT = 3000;

app.get("/", async (req, res) => {
    const code = req.query.code as string;

    if (!code) {
        return res.send("No code received");
    }

    console.log("Received code:", code);

    const tokenData = await getAccessToken(code);

    const accessToken = tokenData?.access_token;
    console.log("Access Token Response:", tokenData);

    if (accessToken) {
        const candles = await getCandleData(accessToken);
        console.log("Candle Data:", candles);
        const raw = candles?.data?.candles || [];
        const normalized = normalizeCandles(raw);
        console.log("Normalized Candles:", normalized.slice(0, 5));
    }

    res.send("Token received! Check console.");
});

app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});