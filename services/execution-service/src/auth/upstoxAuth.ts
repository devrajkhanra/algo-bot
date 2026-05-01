// algo-bot/services/execution-service/src/auth/upstoxAuth.ts

import axios from 'axios';

export class UpstoxAuth {
  private apiKey: string;
  private apiSecret: string;
  private redirectUri: string;
  private baseUrl = 'https://api.upstox.com/v2/login/authorization';

  constructor() {
    this.apiKey = process.env.UPSTOX_API_KEY!;
    this.apiSecret = process.env.UPSTOX_API_SECRET!;
    this.redirectUri = process.env.UPSTOX_REDIRECT_URI!;

    if (!this.apiKey || !this.apiSecret || !this.redirectUri) {
      throw new Error("Missing Upstox OAuth environment variables.");
    }
  }

  /**
   * Generates the URL you will click every morning to authorize the bot.
   */
  getLoginUrl(): string {
    return `${this.baseUrl}/dialog?response_type=code&client_id=${this.apiKey}&redirect_uri=${this.redirectUri}`;
  }

  /**
   * Exchanges the callback code for a live access token.
   */
  async getAccessToken(code: string): Promise<string> {
    const payload = new URLSearchParams({
      code,
      client_id: this.apiKey,
      client_secret: this.apiSecret,
      redirect_uri: this.redirectUri,
      grant_type: 'authorization_code',
    });

    try {
      const response = await axios.post(`${this.baseUrl}/token`, payload.toString(), {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Accept': 'application/json',
        },
      });
      return response.data.access_token;
    } catch (error: any) {
      console.error('[UpstoxAuth] Failed to fetch access token:', error.response?.data || error.message);
      throw error;
    }
  }
}