// algo-bot/services/data-service/src/utils/protobufDecoder.ts

/**
 * MOCK UTILITY: Decodes Upstox Protobuf binary data into JSON.
 * TODO: Implement actual protobuf decoding using Upstox's MarketDataFeed.proto schema
 */
export function decodeMarketData(buffer: Buffer): any {
  // In production, this will use protobufjs to decode the buffer.
  // For now, we return a mocked structure to satisfy the FeedManager.
  console.warn("Mock protobuf decoder called. Need to implement real schema.");
  return {
    feeds: {} 
  };
}