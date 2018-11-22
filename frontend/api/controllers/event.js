'use strict';

const util = require('util');

module.exports = {
  event: event
};

/*
  Functions in a127 controllers used for operations should take two parameters:

  Param 1: a handle to the request object
  Param 2: a handle to the response object
 */
function event(req, res) {
  let name = undefined;

  // variables defined in the Swagger document can be referenced using req.swagger.params.{parameter_name}
  if (req.swagger.params != undefined)
  {
    name = req.swagger.params.year.value || '';
  }

  // this sends back a JSON response which is a single string
  res.json("Hello, Response!");
}
