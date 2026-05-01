// algo-bot/services/execution-service/src/clients/UpstoxClient.ts

import axios, { AxiosInstance } from 'axios';

export interface UpstoxOrderPayload {
  quantity: number;
  product: 'I' | 'D';
  validity: 'DAY' | 'IOC';
  price: number;
  tag: string;
  instrument_token: string;
  order_type: 'MARKET' | 'LIMIT' | 'SL' | 'SL-M';
  transaction_type: 'BUY' | 'SELL';
  disclosed_quantity: number;
  trigger_price: number;
  is_amo: boolean;
}

export class UpstoxClient {
  private client: AxiosInstance;

  constructor(accessToken: string) {
    if (!accessToken) throw new Error("Upstox API token is required.");
    
    this.client = axios.create({
      baseURL: process.env.UPSTOX_API_URL || 'https://api.upstox.com/v2',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      timeout: 5000 // Fail fast on execution
    });
  }

  async placeOrder(payload: UpstoxOrderPayload): Promise<string> {
    try {
      const response = await this.client.post('/order/place', payload);
      if (response.data.status === 'success') {
        return response.data.data.order_id;
      }
      throw new Error(`Upstox API Error: ${response.data.message}`);
    } catch (error: any) {
      // Log explicit error details for monitoring
      console.error(`[UpstoxClient] Order placement failed: ${error.message}`);
      throw error;
    }
  }

  /**
   * Safe, read-only method to verify API connectivity and token validity.
   */
  async getProfile(): Promise<any> {
    try {
      const response = await this.client.get('/user/profile');
      return response.data;
    } catch (error: any) {
      console.error(`[UpstoxClient] Profile fetch failed: ${error.response?.data?.message || error.message}`);
      throw error;
    }
  }
}