import axios from "axios";
import dotenv from "dotenv";
dotenv.config();

export const getAccessToken = async (code: string) => {
  try {
    const response = await axios.post(
      "https://api.upstox.com/v2/login/authorization/token",
      {
        code,
        client_id: process.env.UPSTOX_API_KEY,
        client_secret: process.env.UPSTOX_API_SECRET,
        redirect_uri: process.env.UPSTOX_REDIRECT_URI,
        grant_type: "authorization_code",
      },
      {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      }
    );

    return response.data;
  } catch (err: any) {
    console.error(err.response?.data || err.message);
  }
};