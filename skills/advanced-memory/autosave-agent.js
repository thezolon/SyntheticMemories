#!/usr/bin/env node

/**
 * Auto-save Memory Agent
 * Monitors main session and stores messages to advanced-memory service
 */

const fs = require('fs');
const path = require('path');
const http = require('http');

const SERVICE_URL = 'http://localhost:8768';
const BATCH_SIZE = 20;
const BATCH_FLUSH_MS = 2 * 60 * 1000; // 2 minutes
const HEALTH_CHECK_INTERVAL = 5 * 60 * 1000; // 5 minutes
const RETRY_ATTEMPTS = 3;
const RETRY_BACKOFF_MS = 1000;

const DATA_DIR = path.join(__dirname, 'data');
const FAILURE_LOG = path.join(DATA_DIR, 'autosave_failures.log');

// Ensure data directory exists
if (!fs.existsSync(DATA_DIR)) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}

// State
let batch = [];
let flushTimer = null;
let serviceHealthy = true;
let lastHealthCheck = 0;

/**
 * Log failure to file
 */
function logFailure(message, error) {
  const timestamp = new Date().toISOString();
  const entry = `[${timestamp}] ${message}\n${error}\n\n`;
  fs.appendFileSync(FAILURE_LOG, entry);
}

/**
 * Make HTTP request
 */
function httpRequest(method, path, data = null) {
  return new Promise((resolve, reject) => {
    const url = new URL(path, SERVICE_URL);
    const options = {
      method,
      headers: data ? { 'Content-Type': 'application/json' } : {}
    };

    const req = http.request(url, options, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(body ? JSON.parse(body) : null);
        } else {
          reject(new Error(`HTTP ${res.statusCode}: ${body}`));
        }
      });
    });

    req.on('error', reject);
    if (data) req.write(JSON.stringify(data));
    req.end();
  });
}

/**
 * Check service health
 */
async function checkHealth() {
  try {
    await httpRequest('GET', '/health');
    if (!serviceHealthy) {
      console.log('✅ Advanced-memory service is healthy again');
      serviceHealthy = true;
    }
    return true;
  } catch (error) {
    if (serviceHealthy) {
      console.error('⚠️ Advanced-memory service is unhealthy, pausing autosave');
      serviceHealthy = false;
    }
    return false;
  }
}

/**
 * Score message importance (0-10)
 */
function scoreImportance(message) {
  const text = message.text || '';
  let score = 4; // Base score

  // Scoring heuristics
  if (text.length > 500) score += 1;
  if (text.length > 1000) score += 1;
  
  // Keywords that indicate importance
  const importantKeywords = ['remember', 'important', 'critical', 'note', 'todo', 'decision'];
  const hasImportantKeyword = importantKeywords.some(kw => text.toLowerCase().includes(kw));
  if (hasImportantKeyword) score += 2;

  // Questions might be important
  if (text.includes('?')) score += 1;

  // Commands or technical content
  if (text.includes('```') || text.includes('`')) score += 1;

  // Code blocks or structured data
  if (text.match(/^[\s]*[-*]\s/m) || text.match(/^\d+\./m)) score += 1;

  // URLs suggest reference material
  if (text.match(/https?:\/\//)) score += 1;

  return Math.min(10, Math.max(0, score));
}

/**
 * Determine storage tier based on score
 */
function getTier(score) {
  if (score <= 3) return null; // Don't store
  if (score <= 6) return 'session';
  if (score <= 8) return 'user';
  return 'global';
}

/**
 * Store message with retries
 */
async function storeMessage(message, attempt = 1) {
  try {
    const result = await httpRequest('POST', '/store', message);
    return result;
  } catch (error) {
    if (attempt < RETRY_ATTEMPTS) {
      const delay = RETRY_BACKOFF_MS * Math.pow(2, attempt - 1);
      await new Promise(resolve => setTimeout(resolve, delay));
      return storeMessage(message, attempt + 1);
    }
    throw error;
  }
}

/**
 * Flush batch to service
 */
async function flushBatch() {
  if (batch.length === 0) return;
  
  const toStore = batch.splice(0, batch.length);
  
  for (const item of toStore) {
    try {
      const result = await storeMessage(item);
      const excerpt = item.content.substring(0, 60).replace(/\n/g, ' ');
      console.log(`📝 Stored [${item.tier}] score=${item.importance} id=${result.memory_id} "${excerpt}..."`);
    } catch (error) {
      logFailure(`Failed to store message (tier=${item.tier}, score=${item.importance})`, error.message);
      console.error(`❌ Failed to store message: ${error.message}`);
    }
  }
}

/**
 * Schedule batch flush
 */
function scheduleBatchFlush() {
  if (flushTimer) clearTimeout(flushTimer);
  flushTimer = setTimeout(flushBatch, BATCH_FLUSH_MS);
}

/**
 * Process incoming message
 */
async function processMessage(msg) {
  // Check service health periodically
  const now = Date.now();
  if (now - lastHealthCheck > HEALTH_CHECK_INTERVAL) {
    await checkHealth();
    lastHealthCheck = now;
  }

  if (!serviceHealthy) {
    return; // Skip while service is unhealthy
  }

  // Extract message details
  const content = msg.text || msg.content || '';
  if (!content.trim()) return; // Skip empty messages

  // Score importance
  const importance = scoreImportance(msg);
  const tier = getTier(importance);

  if (!tier) {
    // Don't store low-importance messages
    return;
  }

  // Prepare storage payload
  const payload = {
    content,
    importance,
    tier,
    metadata: {
      source: 'telegram',
      timestamp: msg.timestamp || new Date().toISOString(),
      conversation_id: msg.conversation_id || 'main',
      message_id: msg.message_id || null,
      auto_scored: true
    }
  };

  // Add to batch
  batch.push(payload);

  // Flush if batch is full
  if (batch.length >= BATCH_SIZE) {
    await flushBatch();
  } else {
    scheduleBatchFlush();
  }
}

/**
 * Monitor session messages
 * This is a simplified simulation - in production, this would hook into
 * the OpenClaw message bus or session event stream
 */
async function monitorSession() {
  console.log('🤖 Auto-save memory agent started');
  console.log(`📊 Policy: score 0-3=skip, 4-6=session, 7-8=user, 9-10=global`);
  console.log(`📦 Batching: max ${BATCH_SIZE} items or ${BATCH_FLUSH_MS/1000}s`);
  console.log(`🔄 Retries: ${RETRY_ATTEMPTS}x with exponential backoff`);
  console.log(`💾 Failure log: ${FAILURE_LOG}`);
  console.log('');

  // Initial health check
  await checkHealth();

  // In a real implementation, this would subscribe to the session message stream
  // For now, we'll monitor stdin as a simulation
  console.log('📡 Monitoring session messages (paste JSON messages or type "test" for demo)...\n');

  process.stdin.setEncoding('utf8');
  process.stdin.on('data', async (data) => {
    const line = data.trim();
    
    if (line === 'test') {
      // Demo message
      await processMessage({
        text: 'This is a test message for the auto-save agent',
        timestamp: new Date().toISOString(),
        conversation_id: 'main',
        message_id: 'test-' + Date.now()
      });
      return;
    }

    if (line === 'flush') {
      await flushBatch();
      console.log('✅ Batch flushed manually');
      return;
    }

    if (line === 'health') {
      const healthy = await checkHealth();
      console.log(`Health: ${healthy ? '✅ healthy' : '❌ unhealthy'}`);
      return;
    }

    if (line === 'quit' || line === 'exit') {
      await flushBatch();
      console.log('👋 Auto-save agent stopping...');
      process.exit(0);
    }

    // Try to parse as JSON message
    try {
      const msg = JSON.parse(line);
      await processMessage(msg);
    } catch (e) {
      // Ignore parse errors
    }
  });

  // Flush on exit
  process.on('SIGINT', async () => {
    console.log('\n⚠️ Received SIGINT, flushing batch...');
    await flushBatch();
    process.exit(0);
  });

  process.on('SIGTERM', async () => {
    console.log('\n⚠️ Received SIGTERM, flushing batch...');
    await flushBatch();
    process.exit(0);
  });

  // Keep alive
  setInterval(() => {}, 1000);
}

// Start monitoring
monitorSession().catch(error => {
  console.error('💥 Fatal error:', error);
  logFailure('Fatal error in auto-save agent', error.message);
  process.exit(1);
});
