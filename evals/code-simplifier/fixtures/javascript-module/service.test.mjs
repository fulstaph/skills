import test from 'node:test';
import assert from 'node:assert/strict';
import { processItems } from './service.mjs';

test('processing preserves sequential effects and result order', async () => {
  const events = [];
  const result = await processItems(['a', 'b'], {
    validate: async item => { events.push(`validate:${item}`); return item.toUpperCase(); },
    save: async item => { events.push(`save:${item}`); return `saved:${item}`; },
    emit: async item => { events.push(`emit:${item}`); },
  });
  assert.deepEqual(events, ['validate:a', 'save:A', 'emit:saved:A', 'validate:b', 'save:B', 'emit:saved:B']);
  assert.deepEqual(result, ['saved:A', 'saved:B']);
});

test('save rejection propagates without emit or later items', async () => {
  const events = [];
  const failure = new Error('save failed');
  await assert.rejects(processItems(['a', 'b'], {
    validate: async item => { events.push(`validate:${item}`); return item; },
    save: async item => { events.push(`save:${item}`); throw failure; },
    emit: async item => { events.push(`emit:${item}`); },
  }), error => error === failure);
  assert.deepEqual(events, ['validate:a', 'save:a']);
});

test('empty input has no effects', async () => {
  const unexpected = () => { throw new Error('unexpected call'); };
  assert.deepEqual(await processItems([], { validate: unexpected, save: unexpected, emit: unexpected }), []);
});
