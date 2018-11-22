'use strict';

const util = require('util');
const models = require("../../models");

/*
 * Responds to a request to the /event endpoint
 */
function event(req, res)
{
  let year;

  // variables defined in the Swagger document can be referenced using
  // req.swagger.params.{parameter_name}

  if (req.swagger.params != undefined && req.swagger.params.year.value != undefined)
  {
    year = req.swagger.params.year.value;
    models.Event.findAll({ where: { year: year } }).then((results, err) => {
      if (err) { console.error(err); }
      res.json(results);
    });
  }
  else
  {
    models.Event.findAll().then((results, err) => {
      if (err) { console.error(err); }
      res.json(results);
    });
  }
}

module.exports = { event: event };
