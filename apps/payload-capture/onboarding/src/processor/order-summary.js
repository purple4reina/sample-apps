'use strict';

// Derives a small summary from a placed order. This is stand-in business
// logic for the processor — unlike the incident app's settlement processor,
// there is no validation branch that throws. The point of this service is
// steady, healthy traffic with a rich payload, not an error path.

function summarizeOrder(order) {
  const itemCount = order.order.lineItems.reduce((sum, item) => sum + item.quantity, 0);
  return {
    orderId: order.order.id,
    store: order.store,
    channel: order.channel,
    fulfillmentType: order.order.fulfillmentType,
    itemCount,
    totalCents: order.order.totalCents,
  };
}

module.exports = { summarizeOrder };
