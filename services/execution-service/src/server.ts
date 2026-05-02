// algo-bot/services/execution-service/src/server.ts

import * as dotenv from 'dotenv';
dotenv.config();

import express from 'express';
import { UpstoxAuth } from './auth/upstoxAuth.js';
import { UpstoxClient } from './clients/UpstoxClient.js';
import { OrderManager } from './services/OrderManager.js';
import { RedisEventBus, EventTopic } from '@algo-bot/shared';

const app = express();
const port = 3000;

const auth = new UpstoxAuth();
const eventBus = new RedisEventBus();


// Global state for the execution service (will move to Redis later)
export let upstoxClient: UpstoxClient | null = null;
export let orderManager: OrderManager | null = null;

// 1. Visit this route to start the day
app.get('/api/auth/login', (req, res) => {
  const loginUrl = auth.getLoginUrl();
  console.log(`[Server] Redirecting to Upstox Login...`);
  res.redirect(loginUrl);
});

// 2. Upstox redirects back here with the authorization code
app.get('/api/auth/callback', async (req, res) => {
  const code = req.query.code as string;
  if (!code) return res.status(400).send('Authorization code missing.');

  try {
    console.log(`[Server] Received Auth Code. Exchanging for Token...`);
    const accessToken = await auth.getAccessToken(code);
    
    // Initialize Execution System
    upstoxClient = new UpstoxClient(accessToken);
    orderManager = new OrderManager(upstoxClient);

    console.log(`[Server] ✅ System Initialized. Execution Service is LIVE.`);
    
    // ---> NEW: BROADCAST THE TOKEN TO THE REST OF THE SYSTEM <---
    await eventBus.publish(EventTopic.AUTH_TOKEN_UPDATED, { token: accessToken });
    console.log(`[Server] 📡 Access Token broadcasted to Redis bus.`);

    const profile = await upstoxClient.getProfile();
    res.send(`<h1>Authentication Successful</h1><p>Bot is connected as ${profile.data.user_name}.</p>`);
    
  } catch (error) {
    res.status(500).send('Failed to authenticate with Upstox.');
  }
});

app.listen(port, () => {
  console.log(`🚀 Execution Service Auth Server running on http://localhost:${port}`);
  console.log(`👉 START YOUR DAY: Visit http://localhost:${port}/api/auth/login to authenticate the bot.`);
});