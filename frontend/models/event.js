"use strict";

module.exports = (sequelize, DataTypes) => {
  return sequelize.define("Event", {
    _id: { type: DataTypes.BIGINT, primaryKey: true },
    year: DataTypes.INTEGER,
    era: DataTypes.STRING,
    month: DataTypes.INTEGER,
    day: DataTypes.INTEGER,
    text: DataTypes.TEXT,
    type: DataTypes.STRING
  },
  {
    tableName: "events",
    timestamps: false
  });
};
