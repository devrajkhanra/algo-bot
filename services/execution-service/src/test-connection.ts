// algo-bot/services/execution-service/src/test-connection.ts

import { UpstoxClient } from './clients/UpstoxClient.js';
import * as dotenv from 'dotenv';

// Load environment variables from the .env file in execution-service
dotenv.config(); 

async function runConnectionTest() {
  const token = process.env.UPSTOX_ACCESS_TOKEN;
  
  if (!token) {
    console.error("❌ ERROR: UPSTOX_ACCESS_TOKEN is not defined in your .env file.");
    process.exit(1);
  }

  console.log("🔄 Initializing connection to Upstox API...");
  const client = new UpstoxClient(token);

  try {
    const profileResponse = await client.getProfile();
    console.log("✅ Connection Successful! Broker accepted the token.");
    console.log("👤 User ID:", profileResponse.data.user_id);
    console.log("👤 Name:", profileResponse.data.user_name);
    console.log("------------------------------------------------");
  } catch (error) {
    console.error("❌ Connection Failed. Please verify your token and network.");
  }
}

runConnectionTest();