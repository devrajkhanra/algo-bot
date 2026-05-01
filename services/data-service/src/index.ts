// algo-bot/services/data-service/src/index.ts

import { RedisEventBus, EventTopic } from '@algo-bot/shared';
import { UpstoxFeedClient } from './clients/UpstoxFeedClient';
import { FeedManager } from './services/FeedManager';

async function startDataService() {
  console.log('🔄 Starting Data Service... waiting for auth token from Redis.');
  
  const redisBus = new RedisEventBus();

  // Listen for the morning token broadcast
  await redisBus.subscribe<{ token: string }>(
    EventTopic.AUTH_TOKEN_UPDATED, 
    (payload) => {
      console.log('🔑 Received Auth Token from Event Bus. Initializing WebSocket...');
      
      // Inject the token into the environment so UpstoxFeedClient can use it
      process.env.UPSTOX_ACCESS_TOKEN = payload.token;

      // Upstox WebSocket URL for API v2
      const wsUrl = 'wss://api.upstox.com/v2/feed/market-data-feed';
      
      const feedClient = new UpstoxFeedClient(wsUrl);
      const feedManager = new FeedManager(feedClient /*, redisBus */);
      
      feedClient.connect();

      // For testing, subscribe to a highly liquid instrument (e.g., Nifty 50 Index or Reliance)
      // Note: You need the exact instrumentKey from Upstox's instrument list CSV
      feedClient.on('connected', () => {
         console.log('📈 WebSocket connected. Subscribing to default instruments...');
         // feedClient.subscribe(['NSE_EQ|INE002A01018']); // Example: Reliance
      });
    }
  );
}

startDataService().catch(console.error);