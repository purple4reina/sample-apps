'use strict';

// Builds a single `order.placed` event for the storefront producer. Every
// call is independent and random — there is no drift/generation argument
// here, unlike the incident app's `buildMessage(generation)`. This service
// ships in one steady, healthy shape; the point is realistic breadth
// (nesting, arrays, enums, sparse fields), not a format that changes over
// time.

const crypto = require('crypto');

const STORES = {
  'storefront-us': { currency: 'USD', homeCountry: 'US' },
  'storefront-eu': { currency: 'EUR', homeCountry: 'DE' },
  'storefront-uk': { currency: 'GBP', homeCountry: 'GB' },
  'storefront-jp': { currency: 'JPY', homeCountry: 'JP' },
};
const STORE_NAMES = Object.keys(STORES);

const CHANNELS = weighted([
  ['web', 0.45],
  ['ios', 0.2],
  ['android', 0.2],
  ['pos', 0.05],
  ['marketplace', 0.1],
]);

const LOYALTY_TIERS = weighted([
  ['none', 0.35],
  ['bronze', 0.3],
  ['silver', 0.2],
  ['gold', 0.1],
  ['platinum', 0.05],
]);

const CATEGORIES = weighted([
  ['apparel', 0.22],
  ['electronics', 0.16],
  ['home-goods', 0.14],
  ['beauty', 0.12],
  ['outdoors', 0.12],
  ['toys-games', 0.1],
  ['grocery', 0.08],
  ['digital-media', 0.06],
]);

const PRODUCT_NAMES = {
  apparel: ['Trailhead Rain Jacket', 'Classic Crew Tee', 'Ridgeline Fleece Vest'],
  electronics: ['NoiseAway Headphones', 'PowerBank 10K', 'Compact Bluetooth Speaker'],
  'home-goods': ['Cast Iron Skillet', 'Linen Throw Blanket', 'Ceramic Pour-Over Set'],
  beauty: ['Daily Mineral SPF 30', 'Hydrating Face Serum', 'Bamboo Bristle Brush Set'],
  outdoors: ['Trail Running Backpack', '2-Person Tent', 'Insulated Water Bottle'],
  'toys-games': ['Wooden Building Blocks', 'Strategy Board Game', 'RC Stunt Car'],
  grocery: ['Single-Origin Coffee Beans', 'Organic Trail Mix', 'Cold-Pressed Olive Oil'],
  'digital-media': ['Focus Timer Pro (annual)', 'Photo Editing Suite License', 'Audiobook Credit Bundle'],
};

const PAYMENT_METHODS = weighted([
  ['credit_card', 0.45],
  ['paypal', 0.2],
  ['apple_pay', 0.15],
  ['google_pay', 0.1],
  ['gift_card', 0.06],
  ['store_credit', 0.04],
]);

const SHIPPING_METHODS = weighted([
  ['standard', 0.7],
  ['expedited', 0.22],
  ['overnight', 0.08],
]);

const PROMO_CODES = [
  { code: 'WELCOME10', type: 'percent', percentOff: 10 },
  { code: 'SUMMER15', type: 'percent', percentOff: 15 },
  { code: 'FREESHIP', type: 'shipping', percentOff: 0 },
];

const EXPERIMENTS = [
  { name: 'checkout-redesign-2026', variants: ['control', 'treatment-a', 'treatment-b'] },
  { name: 'search-ranking-v3', variants: ['control', 'treatment'] },
];

const USER_AGENTS = [
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15',
  'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15',
  'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36',
];

// Builds a weighted picker from `[value, weight]` pairs.
function weighted(pairs) {
  const total = pairs.reduce((sum, [, w]) => sum + w, 0);
  return () => {
    let r = Math.random() * total;
    for (const [value, w] of pairs) {
      r -= w;
      if (r <= 0) return value;
    }
    return pairs[pairs.length - 1][0];
  };
}

function pick(arr) {
  return arr[crypto.randomInt(arr.length)];
}

function randomHexId(prefix, bytes) {
  return `${prefix}_${crypto.randomBytes(bytes).toString('hex')}`;
}

function randomIPv4() {
  return [10 + crypto.randomInt(240), crypto.randomInt(256), crypto.randomInt(256), 1 + crypto.randomInt(254)].join('.');
}

function buildLineItem() {
  const category = CATEGORIES();
  const digital = category === 'digital-media';
  const unitPriceCents = digital ? 999 + crypto.randomInt(4000) : 1499 + crypto.randomInt(15000);
  return {
    sku: randomHexId('sku', 4),
    productName: pick(PRODUCT_NAMES[category]),
    category,
    quantity: digital ? 1 : 1 + crypto.randomInt(3),
    unitPriceCents,
    digital,
  };
}

function buildOrderPlacedEvent() {
  const storeName = pick(STORE_NAMES);
  const store = STORES[storeName];

  const lineItemCount = 1 + crypto.randomInt(4);
  const lineItems = Array.from({ length: lineItemCount }, buildLineItem);
  const allDigital = lineItems.every((item) => item.digital);
  const noneDigital = lineItems.every((item) => !item.digital);
  const fulfillmentType = allDigital ? 'digital' : noneDigital ? 'physical' : 'mixed';

  const subtotalCents = lineItems.reduce((sum, item) => sum + item.unitPriceCents * item.quantity, 0);
  const hasPromotion = Math.random() > 0.7;
  const promotions = hasPromotion ? [pick(PROMO_CODES)] : undefined;
  const discountCents = hasPromotion && promotions[0].type === 'percent'
    ? Math.round((subtotalCents * promotions[0].percentOff) / 100)
    : 0;
  const shippingCents = fulfillmentType === 'digital' ? 0 : 599 + crypto.randomInt(1000);
  const taxCents = Math.round((subtotalCents - discountCents) * 0.08);
  const totalCents = subtotalCents - discountCents + taxCents + shippingCents;

  const paymentMethod = PAYMENT_METHODS();

  const shipping = fulfillmentType !== 'digital' ? {
    address: {
      line1: `${100 + crypto.randomInt(9000)} Alder Street`,
      city: 'Portland',
      region: 'OR',
      postalCode: String(97201 + crypto.randomInt(99)),
      country: store.homeCountry,
    },
    method: SHIPPING_METHODS(),
    estimatedDeliveryDate: new Date(Date.now() + (2 + crypto.randomInt(6)) * 86400000).toISOString().slice(0, 10),
  } : undefined;

  const hasExperiment = Math.random() > 0.5;
  const experiments = hasExperiment ? (() => {
    const experiment = pick(EXPERIMENTS);
    return [{ name: experiment.name, variant: pick(experiment.variants) }];
  })() : undefined;

  return {
    schemaVersion: '1',
    eventId: crypto.randomUUID(),
    eventType: 'order.placed',
    occurredAt: new Date().toISOString(),
    store: storeName,
    channel: CHANNELS(),
    customer: {
      id: randomHexId('cus', 6),
      loyaltyTier: LOYALTY_TIERS(),
      firstOrder: Math.random() < 0.2,
    },
    order: {
      id: randomHexId('ord', 6),
      currency: store.currency,
      fulfillmentType,
      subtotalCents,
      discountCents,
      taxCents,
      shippingCents,
      totalCents,
      lineItems,
      ...(promotions ? { promotions } : {}),
    },
    payment: {
      method: paymentMethod,
      giftCardApplied: paymentMethod === 'gift_card' || Math.random() < 0.05,
    },
    ...(shipping ? { shipping } : {}),
    device: {
      ip: randomIPv4(),
      userAgent: pick(USER_AGENTS),
      sessionId: crypto.randomUUID(),
    },
    ...(experiments ? { experiments } : {}),
  };
}

module.exports = { buildOrderPlacedEvent };
