// algo-bot/services/data-service/src/utils/protobufDecoder.ts

import * as protobuf from 'protobufjs';
import * as path from 'path';

// Pre-load the schema into memory when the service starts
const protoPath = path.resolve(__dirname, '../proto/MarketDataFeed.proto');
const root = protobuf.loadSync(protoPath);
const FeedResponse = root.lookupType('com.upstox.marketdatafeeder.rpc.proto.FeedResponse');

export function decodeMarketFeed(buffer: Buffer): any {
  try {
    // Decode the binary blob
    const message = FeedResponse.decode(buffer);
    
    // Convert it to a readable JavaScript object
    const decodedObject = FeedResponse.toObject(message, {
      longs: String,
      enums: String,
      bytes: String,
    });
    
    return decodedObject;
  } catch (error) {
    console.error('[ProtobufDecoder] Error decoding feed:', error);
    return null;
  }
}