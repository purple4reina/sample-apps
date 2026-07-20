'use strict';

// The producer stands in for an upstream "ledger-core" service owned by another
// team. It emits settlement messages onto the queue. The exact wire format it
// produces is selected at runtime by the `generation` argument (see handler.js),
// which lets us simulate an upstream rolling out a new record format without any
// change to the downstream processor.

const crypto = require('crypto');

const REGIONS = ['US', 'EU', 'GB', 'JP'];
const SCHEMES = ['A', 'W', 'C', 'S']; // ACH, Wire, Card, SEPA
const CURRENCIES = { US: 'USD', EU: 'EUR', GB: 'GBP', JP: 'JPY' };
const COUNTERPARTIES = [
  { id: 'CP-7A31', name: 'Meridian Clearing' },
  { id: 'CP-1F09', name: 'Halcyon Capital' },
  { id: 'CP-B4C2', name: 'Northwind Securities' },
  { id: 'CP-9D77', name: 'Copperline Bank' },
  { id: 'CP-5E60', name: 'Ridgeway Partners' },
];

function pick(arr) {
  return arr[crypto.randomInt(arr.length)];
}

function pad(value, width) {
  return String(value).padStart(width, '0');
}

// A settlement reference is a positional (fixed-width) composite key:
//   [region:2][ledgerId:6][sequence:N][scheme:1]
// `sequenceWidth` is what changes between format generations.
function buildRef(parts, sequenceWidth, scheme) {
  return (
    parts.region +
    pad(parts.ledgerId, 6) +
    pad(parts.sequence % 10 ** sequenceWidth, sequenceWidth) +
    scheme
  );
}

function isoDate(offsetDays) {
  const d = new Date(Date.now() + offsetDays * 86400000);
  return d.toISOString().slice(0, 10); // YYYY-MM-DD
}

function usDate(offsetDays) {
  const d = new Date(Date.now() + offsetDays * 86400000);
  const mm = pad(d.getUTCMonth() + 1, 2);
  const dd = pad(d.getUTCDate(), 2);
  return `${mm}/${dd}/${d.getUTCFullYear()}`; // MM/DD/YYYY
}

// Build a single settlement message in the requested generation.
function buildMessage(generation) {
  const region = pick(REGIONS);
  const parts = {
    region,
    ledgerId: crypto.randomInt(1000000),
    sequence: crypto.randomInt(100000000), // 8 significant digits
  };
  const scheme = pick(SCHEMES);
  const offsetDays = crypto.randomInt(5) - 2; // -2..+2 days around today
  const counterparty = pick(COUNTERPARTIES);

  const settlement = {
    ref: buildRef(parts, 8, scheme),
    valueDate: isoDate(offsetDays),
    amountMinor: 1000 + crypto.randomInt(9_999_000),
    currency: CURRENCIES[region],
  };

  const message = {
    schemaVersion: '1',
    messageId: crypto.randomUUID(),
    emittedAt: new Date().toISOString(),
    origin: 'ledger-core',
    settlement,
    counterparty: { id: counterparty.id, name: counterparty.name },
  };

  switch (generation) {
    case 'next':
      // Sequence range outgrew 8 digits; the field is now emitted 10 wide.
      settlement.ref = buildRef(parts, 10, scheme);
      break;
    case 'scheme-case':
      settlement.ref = buildRef(parts, 8, scheme.toLowerCase());
      break;
    case 'datetime':
      settlement.valueDate = usDate(offsetDays);
      break;
    case 'counterparty':
      message.counterparty = { id: { value: counterparty.id, scheme: 'LEI' }, name: counterparty.name };
      break;
    case 'stable':
    default:
      break;
  }

  return message;
}

module.exports = { buildMessage };
