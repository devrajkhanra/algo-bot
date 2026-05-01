// algo-bot/services/execution-service/src/services/OrderManager.ts

import { OrderIntent, OrderStateUpdate } from '@algo-bot/shared';
import { UpstoxClient, UpstoxOrderPayload } from '../clients/UpstoxClient.js';

export class OrderManager {
  private upstoxClient: UpstoxClient;

  constructor(upstoxClient: UpstoxClient) {
    this.upstoxClient = upstoxClient;
  }

  /**
   * Translates internal OrderIntent to Upstox format and executes.
   */
  async executeIntent(intent: OrderIntent): Promise<OrderStateUpdate> {
    const payload = this.mapIntentToUpstoxPayload(intent);

    try {
      const brokerOrderId = await this.upstoxClient.placeOrder(payload);
      
      return {
        intentId: intent.intentId,
        brokerOrderId,
        status: 'PENDING', // Will be updated to OPEN/FILLED via websocket stream later
        filledQuantity: 0,
        timestamp: Date.now()
      };
    } catch (error: any) {
      // Handle execution-level failure (e.g., API down, token expired)
      return {
        intentId: intent.intentId,
        status: 'REJECTED',
        filledQuantity: 0,
        message: error.message,
        timestamp: Date.now()
      };
    }
  }

  private mapIntentToUpstoxPayload(intent: OrderIntent): UpstoxOrderPayload {
    return {
      instrument_token: intent.instrumentToken,
      transaction_type: intent.side,
      order_type: intent.type,
      product: intent.product,
      quantity: intent.quantity,
      price: intent.price || 0,
      trigger_price: intent.triggerPrice || 0,
      validity: 'DAY', // Hardcoded for intraday unless specified otherwise
      disclosed_quantity: 0,
      is_amo: false,
      tag: intent.intentId.substring(0, 20) // Upstox allows max 20 chars for tracking tags
    };
  }
}