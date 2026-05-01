// algo-bot/shared/types/index.ts

export type OrderSide = 'BUY' | 'SELL';
export type OrderType = 'MARKET' | 'LIMIT' | 'SL' | 'SL-M';
export type ProductType = 'I' | 'D'; // Intraday (MIS) vs Delivery (CNC)
export type OrderStatus = 'PENDING' | 'OPEN' | 'REJECTED' | 'FILLED' | 'CANCELLED';

// Input: Received from the Risk Service after validation
export interface OrderIntent {
  intentId: string;       // Unique ID for internal tracking (e.g., UUID)
  strategyId: string;     // Which strategy generated this
  instrumentToken: string;// Upstox specific token (e.g., NSE_EQ|INE123...)
  side: OrderSide;
  type: OrderType;
  product: ProductType;
  quantity: number;
  price?: number;         // Required for LIMIT / SL
  triggerPrice?: number;  // Required for SL / SL-M
}

// Output: Published back to the Event Bus
export interface OrderStateUpdate {
  intentId: string;
  brokerOrderId?: string; // Provided by Upstox
  status: OrderStatus;
  filledQuantity: number;
  averagePrice?: number;
  message?: string;       // Rejection reason or API error
  timestamp: number;
}

export interface MarketTick {
  instrumentToken: string;
  timestamp: number;
  lastTradedPrice: number;
  lastTradedQuantity: number;
  averageTradedPrice: number;
  volume: number;
  open: number;
  high: number;
  low: number;
  close: number;
}

export enum EventTopic {
  MARKET_TICK = 'market.tick',           // Followed by instrument token: market.tick.NSE_EQ|INE123
  ORDER_INTENT = 'order.intent',         // Published by strategy, consumed by execution/risk
  ORDER_STATE_UPDATE = 'order.state',    // Published by execution, consumed by strategy/db
  AUTH_TOKEN_UPDATED = 'auth.token_updated'
}