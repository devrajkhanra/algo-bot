// algo-bot/services/execution-service/src/server.ts

import express from 'express';
import { UpstoxAuth } from './auth/upstoxAuth.js';
import { UpstoxClient } from './clients/UpstoxClient.js';
import { OrderManager } from './services/OrderManager.js';

const app = express();
const port = 3000;
const auth = new UpstoxAuth();

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

  if (!code) {
    return res.status(400).send('Authorization code missing.');
  }

  try {
    console.log(`[Server] Received Auth Code. Exchanging for Token...`);
    const accessToken = await auth.getAccessToken(code);
    
    // Initialize the core system now that we have a token
    upstoxClient = new UpstoxClient(accessToken);
    orderManager = new OrderManager(upstoxClient);

    console.log(`[Server] ✅ System Initialized. Execution Service is LIVE.`);
    
    // Test the connection immediately
    const profile = await upstoxClient.getProfile();
    res.send(`<h1>Authentication Successful</h1><p>Bot is connected as ${profile.data.user_name}. You may close this window.</p>`);
    
  } catch (error) {
    res.status(500).send('Failed to authenticate with Upstox.');
  }
});

app.listen(port, () => {
  console.log(`🚀 Execution Service Auth Server running on http://localhost:${port}`);
  console.log(`👉 START YOUR DAY: Visit http://localhost:${port}/api/auth/login to authenticate the bot.`);
});