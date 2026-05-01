// algo-bot/services/execution-service/src/index.ts

import { OrderManager } from './services/OrderManger.js';
import { UpstoxClient } from './clients/UpstoxClient.js';
// Pseudo-import for event bus
// import { RedisEventBus } from '../../shared/utils/RedisEventBus'; 

async function startExecutionService() {
  const token = process.env.UPSTOX_ACCESS_TOKEN!;
  const upstoxClient = new UpstoxClient(token);
  const orderManager = new OrderManager(upstoxClient);
  
  // const eventBus = new RedisEventBus(process.env.REDIS_URL);
  
  console.log('Execution Service started. Listening for Validated Orders...');

  /*
  eventBus.subscribe('orders.validated', async (intent: OrderIntent) => {
    // 1. Execute via Upstox
    const result = await orderManager.executeIntent(intent);
    
    // 2. Publish state back to the system (for DB logging, risk updates, etc.)
    await eventBus.publish('orders.state_update', result);
  });
  */
}

startExecutionService().catch(console.error);