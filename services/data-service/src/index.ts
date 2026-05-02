// algo-bot/services/data-service/src/index.ts

import { RedisEventBus, EventTopic } from '@algo-bot/shared';
import { UpstoxFeedClient } from './clients/UpstoxFeedClient';
import { FeedManager } from './services/FeedManager';

async function startDataService() {
  console.log('🔄 Starting Data Service... waiting for auth token from Redis.');
  
  const redisBus = new RedisEventBus();

  await redisBus.subscribe<{ token: string }>(
    EventTopic.AUTH_TOKEN_UPDATED, 
    async (payload) => {
      console.log('🔑 Received Auth Token from Event Bus. Fetching dynamic WS URL...');
      
      try {
        process.env.UPSTOX_ACCESS_TOKEN = payload.token;

        // ---> NEW: Fetch the dynamic one-time WebSocket URL from Upstox <---
        const response = await fetch('https://api.upstox.com/v3/feed/market-data-feed/authorize', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${payload.token}`,
            'Accept': 'application/json'
          }
        });

        const authData = await response.json();

        if (authData.status !== 'success' || !authData.data?.authorized_redirect_uri) {
            throw new Error(`Upstox WS Auth Failed: ${JSON.stringify(authData)}`);
        }

        const dynamicWsUrl = authData.data.authorized_redirect_uri;
        console.log('🔗 Acquired authorized WebSocket URI from Upstox. Connecting...');
        
        const feedClient = new UpstoxFeedClient(dynamicWsUrl);
        const feedManager = new FeedManager(feedClient /*, redisBus */);
        
        feedClient.connect();

        feedClient.on('connected', () => {
           console.log('📈 WebSocket connected successfully.');

           feedClient.subscribe(['NSE_INDEX|Nifty 50'], 'ltpc');
        });

      } catch (error) {
        console.error('❌ Failed to initialize WebSocket:', error);
      }
    }
  );
}

startDataService().catch(console.error);