// algo-bot/services/data-service/src/services/FeedManager.ts

import { MarketTick } from '@algo-bot/shared';
import { UpstoxFeedClient } from '../clients/UpstoxFeedClient';
// import { RedisEventBus } from '@algo-bot/shared'; 

export class FeedManager {
  private client: UpstoxFeedClient;
  // private eventBus: RedisEventBus;

  constructor(client: UpstoxFeedClient /*, eventBus: RedisEventBus */) {
    this.client = client;
    // this.eventBus = eventBus;
    this.setupListeners();
  }

  private setupListeners() {
    this.client.on('feed', (rawFeed: any) => {
      // Iterate through the dictionary of instrument feeds returned by Upstox
      for (const [token, data] of Object.entries(rawFeed.feeds)) {
        const tick = this.normalizeTick(token, data as any);
        this.broadcastTick(tick);
      }
    });
  }

  private normalizeTick(instrumentToken: string, data: any): MarketTick {
    // Mapping Upstox full-mode protobuf output to our internal contract
    return {
      instrumentToken,
      timestamp: Date.now(), // Or data.ff.marketFF.exchangeTimeStamp
      lastTradedPrice: data.ff.marketFF.ltpc.ltp,
      lastTradedQuantity: data.ff.marketFF.ltpc.ltq,
      averageTradedPrice: data.ff.marketFF.marketLevel.ffMarketLevel.avgTradedPrice,
      volume: data.ff.marketFF.marketLevel.ffMarketLevel.volume,
      open: data.ff.marketFF.marketLevel.ffMarketLevel.open,
      high: data.ff.marketFF.marketLevel.ffMarketLevel.high,
      low: data.ff.marketFF.marketLevel.ffMarketLevel.low,
      close: data.ff.marketFF.ltpc.cp // previous close
    };
  }

  private async broadcastTick(tick: MarketTick) {
    // await this.eventBus.publish(`market.tick.${tick.instrumentToken}`, tick);
    // console.debug(`Broadcasted tick for ${tick.instrumentToken}: ${tick.lastTradedPrice}`);
  }
}