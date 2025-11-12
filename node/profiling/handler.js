function doSomething() {}

exports.handler = async function(event, context) {
  const end = Date.now() + 65 * 1000
  while (Date.now() < end) { doSomething() }
  return "ok";
}
