'use strict';

const SwaggerExpress = require('swagger-express-mw');
const app = require('express')();
const models = require("./models");

module.exports = app; // for testing

var config = {
  appRoot: __dirname // required config
};

SwaggerExpress.create(config, function(err, swaggerExpress) {
  if (err) { throw err; }

  models.sequelize.sync();

  // install middleware
  swaggerExpress.register(app);

  var port = process.env.PORT || 8080;
  app.listen(port);
});
