// algo-bot/shared/utils/RedisEventBus.ts

import Redis from 'ioredis';

export class RedisEventBus {
  private publisher: Redis;
  private subscriber: Redis;

  constructor(redisUrl: string = 'redis://localhost:6379') {
    this.publisher = new Redis(redisUrl);
    this.subscriber = new Redis(redisUrl);

    this.publisher.on('error', (err) => console.error('[Redis Publisher Error]', err));
    this.subscriber.on('error', (err) => console.error('[Redis Subscriber Error]', err));
  }

  /**
   * Publishes a JSON payload to a specific Redis channel.
   */
  async publish<T>(topic: string, payload: T): Promise<void> {
    try {
      const data = JSON.stringify(payload);
      await this.publisher.publish(topic, data);
    } catch (error) {
      console.error(`[RedisEventBus] Failed to publish to ${topic}:`, error);
      throw error;
    }
  }

  /**
   * Subscribes to a channel (or pattern) and executes the callback on new messages.
   */
  async subscribe<T>(topic: string, callback: (payload: T) => void): Promise<void> {
    // We use psubscribe to allow wildcard topics like "market.tick.*"
    await this.subscriber.psubscribe(topic);

    this.subscriber.on('pmessage', (pattern, channel, message) => {
      if (pattern === topic) {
        try {
          const payload: T = JSON.parse(message);
          callback(payload);
        } catch (error) {
          console.error(`[RedisEventBus] Failed to parse message from ${channel}:`, error);
        }
      }
    });
    
    console.log(`[RedisEventBus] Subscribed to topic pattern: ${topic}`);
  }

  /**
   * Gracefully close connections.
   */
  async disconnect(): Promise<void> {
    await this.publisher.quit();
    await this.subscriber.quit();
  }
}