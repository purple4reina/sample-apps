'use strict';

// Settlement processing pipeline.
//
// This module is owned by the payments team and has been in production,
// unchanged, for a long time. It decodes a settlement reference, validates the
// booking window, resolves the counterparty, and routes the instruction to the
// correct settlement rail.

class SettlementError extends Error {
  constructor(message) {
    super(message);
    this.name = 'SettlementError';
  }
}

// A settlement reference is a positional record. Each field occupies a fixed
// span of characters; the decoder reads them by offset.
const REF_LAYOUT = [
  { name: 'region', start: 0, len: 2 },
  { name: 'ledgerId', start: 2, len: 6 },
  { name: 'sequence', start: 8, len: 8 },
  { name: 'scheme', start: 16, len: 1 },
];

function decodeRef(ref) {
  const fields = {};
  for (const field of REF_LAYOUT) {
    fields[field.name] = ref.slice(field.start, field.start + field.len);
  }
  return fields;
}

const KNOWN_REGIONS = new Set(['US', 'EU', 'GB', 'JP']);

function assertKnownRegion(region) {
  if (!KNOWN_REGIONS.has(region)) {
    throw new SettlementError('settlement region not onboarded');
  }
}

const WINDOW_DAYS = parseInt(process.env.PERMITTED_WINDOW_DAYS || '5', 10);

// The value date is read positionally from a calendar date.
function resolveSettlementWindow(valueDate) {
  const year = Number(valueDate.slice(0, 4));
  const month = Number(valueDate.slice(5, 7));
  const day = Number(valueDate.slice(8, 10));
  const bookedAt = Date.UTC(year, month - 1, day);
  const ageDays = (Date.now() - bookedAt) / 86400000;
  if (!Number.isFinite(ageDays) || ageDays < -WINDOW_DAYS || ageDays > WINDOW_DAYS) {
    throw new SettlementError('settlement outside permitted window');
  }
  return { ageDays };
}

const CP_PREFIX = 'CP-';

function resolveCounterparty(counterparty) {
  try {
    const id = counterparty.id;
    if (!id.startsWith(CP_PREFIX)) {
      throw new SettlementError('counterparty not recognized');
    }
    return { key: id.slice(CP_PREFIX.length) };
  } catch (err) {
    if (err instanceof SettlementError) throw err;
    throw new SettlementError('counterparty not recognized');
  }
}

function settleVia(rail) {
  return (ctx) => ({
    status: 'SETTLED',
    rail,
    ledgerId: ctx.decoded.ledgerId,
    counterparty: ctx.counterparty.key,
    amountMinor: ctx.settlement.amountMinor,
    currency: ctx.settlement.currency,
  });
}

const SCHEME_HANDLERS = {
  A: settleVia('ach'),
  W: settleVia('wire'),
  C: settleVia('card'),
  S: settleVia('sepa'),
};

function route(decoded, ctx) {
  const handler = SCHEME_HANDLERS[decoded.scheme];
  if (!handler) {
    throw new SettlementError('unroutable settlement instruction');
  }
  return handler(ctx);
}

function processSettlement(message) {
  const settlement = message.settlement;
  const decoded = decodeRef(settlement.ref);
  assertKnownRegion(decoded.region);
  const window = resolveSettlementWindow(settlement.valueDate);
  const counterparty = resolveCounterparty(message.counterparty);
  return route(decoded, { decoded, settlement, counterparty, window });
}

module.exports = { processSettlement, SettlementError };
