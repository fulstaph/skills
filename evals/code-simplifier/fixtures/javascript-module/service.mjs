export async function processItems(items, { validate, save, emit }) {
  const results = [];
  for (let index = 0; index < items.length; index += 1) {
    const item = items[index];
    const validatedItem = await validate(item);
    const savedItem = await save(validatedItem);
    await emit(savedItem);
    results.push(savedItem);
  }
  return results;
}
