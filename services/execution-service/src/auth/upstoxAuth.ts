import dotenv from "dotenv";
dotenv.config();

const API_KEY = process.env.UPSTOX_API_KEY!;
const REDIRECT_URI = process.env.UPSTOX_REDIRECT_URI!;

export const getLoginUrl = () => {
  return `https://api.upstox.com/v2/login/authorization/dialog?response_type=code&client_id=${API_KEY}&redirect_uri=${REDIRECT_URI}`;
};