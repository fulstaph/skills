# Simplification tradeoffs

## Preserve missing and false-like values

Python distinguishes `None` from zero. This refactor loses that distinction:

```python
# Before
if amount is None:
    return "missing"
if amount == 0:
    return "zero"

# Unsafe replacement
if not amount:
    return "missing"
```

Keep the explicit checks. Similar care applies to empty strings, booleans,
optional values, and language-specific equality or coercion rules.

## Preserve async effects and failures

```javascript
for (const item of items) {
  const validated = await validate(item);
  const saved = await save(validated);
  await emit(saved);
  results.push(saved);
}
```

This processes one item at a time. If saving fails, that item is not emitted and
later items do not start. Replacing the loop with `Promise.all(items.map(...))`
changes ordering and the work that can occur after a failure. Preserve sequential
execution unless the user has explicitly asked to change that contract.

## Extract a responsibility, not just a line

A helper named `parseAndValidateAddress` can clarify a repeated multi-step
operation with well-defined inputs and outputs. A helper named `getNextValue`
that wraps one obvious expression may add indirection. Judge extraction by how
much a reader must remember, not the number of lines in the calling function.

Keep public names and signatures stable. Trace registered callbacks, reflection,
dynamic dispatch, and configuration references before removing an apparently
unused function. A missing textual call is insufficient evidence of dead code.
