// algo-bot/services/data-service/src/clients/UpstoxFeedClient.ts

import WebSocket from 'ws';
import { EventEmitter } from 'events';
// Assume we have a generated protobuf decoder utility
import { decodeMarketData } from '../utils/protobufDecoder'; 

export class UpstoxFeedClient extends EventEmitter {
  private ws: WebSocket | null = null;
  private wsUrl: string;

  constructor(wsUrl: string) {
    super();
    this.wsUrl = wsUrl;
  }

  connect() {
    this.ws = new WebSocket(this.wsUrl, {
      headers: {
        'Api-Version': '2.0',
        'Authorization': `Bearer ${process.env.UPSTOX_ACCESS_TOKEN}`
      }
    });

    this.ws.on('open', () => {
      console.log('[UpstoxFeedClient] WebSocket connected.');
      this.emit('connected');
    });

    this.ws.on('message', (data: Buffer) => {
      try {
        const decodedFeed = decodeMarketData(data);
        this.emit('feed', decodedFeed);
      } catch (error) {
        console.error('[UpstoxFeedClient] Protobuf decode error:', error);
      }
    });

    this.ws.on('close', () => {
      console.warn('[UpstoxFeedClient] WebSocket closed. Reconnecting...');
      setTimeout(() => this.connect(), 5000); // Simple linear backoff
    });

    this.ws.on('error', (err) => {
      console.error('[UpstoxFeedClient] WebSocket Error:', err.message);
    });
  }

  subscribe(instrumentTokens: string[]) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      throw new Error("Cannot subscribe: WebSocket not connected.");
    }
    
    const payload = {
      guid: "algo-bot-sub",
      method: "sub",
      data: {
        mode: "full", // 'full' gives OHLCV, 'ltp' gives just price
        instrumentKeys: instrumentTokens
      }
    };
    
    this.ws.send(Buffer.from(JSON.stringify(payload)));
  }
}