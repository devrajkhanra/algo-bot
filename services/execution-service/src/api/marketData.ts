import axios from "axios";

export const getCandleData = async (accessToken: string) => {
  try {
    const url =
      "https://api.upstox.com/v2/historical-candle/NSE_EQ|INE002A01018/day/2026-04-30/2026-04-30";

    const response = await axios.get(url, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });

    return response.data;
  } catch (err: any) {
    console.error(err.response?.data || err.message);
  }
};