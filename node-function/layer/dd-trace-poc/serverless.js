// very simple node nodule to allow monkey pathing, could be inlined here
var shimmer = require('shimmer');
const tracer = require("dd-trace");
const axios = require('axios');

tracer.init({
  type: "dog",
});

let handler;
let handlerFunction;

if (process.env.LOCAL_TESTING == "true") {
  handler = require("./dummy_handler.js");
  handlerFunction = "dummyHandler";
} else {
  // let inspect the given handler and require the correct file
  tokens = process.env._HANDLER.split(".");
  var handlerFile = tokens[0];
  // the function name is after the dot
  handlerFunction = tokens[1];
  handler = require(`${process.env.LAMBDA_TASK_ROOT}/${handlerFile}`);
}

shimmer.wrap(handler, handlerFunction, function (original) {
    return function () {
      // we can start the top root span (or notify the extension to do so)
      console.log("[UNIVERSAL INSTRUMENTATION DEMO] - Starting");
      invokeStart(arguments[0]);
      console.log("[UNIVERSAL INSTRUMENTATION DEMO] - Started");

      let res = null
      try {
        // save the original result
        res = original.apply(this, arguments);
      } catch(e) {
        console.log("[UNIVERSAL INSTRUMENTATION DEMO] - Error calling original: ", e);
      } finally {
        console.log("[UNIVERSAL INSTRUMENTATION DEMO] - Ending");
        invokeEnd(res);
        console.log("[UNIVERSAL INSTRUMENTATION DEMO] - Ended");
        return res;
      }
    }
});

function invokeStart(payload) {
  console.log("[UNIVERSAL INSTRUMENTATION DEMO] - invokeStart with payload: ", payload);
  axios
    .post('http://localhost:8124/lambda/start-invocation', payload)
    .then(res => {
      console.log(`[UNIVERSAL INSTRUMENTATION DEMO] - invokeStart statusCode: ${res.status}`);
      console.log("[UNIVERSAL INSTRUMENTATION DEMO] - invokeStart response: ", res);
    })
    .catch(error => {
      console.error(error);
    });
}

function invokeEnd(handlerRes) {
  axios
    .post('http://localhost:8124/lambda/end-invocation', handlerRes)
    .then(res => {
      console.log(`[UNIVERSAL INSTRUMENTATION DEMO] - invokeEnd statusCode: ${res.status}`);
      console.log("[UNIVERSAL INSTRUMENTATION DEMO] - invokeEnd response: ", res);
    })
    .catch(error => {
      console.error("[UNIVERSAL INSTRUMENTATION DEMO] - Error ending invocation: ", error);
    });
}

if (process.env.LOCAL_TESTING == "true") {
  handler.dummyHandler({"pay": "load"}, {"con": "text"});
}
