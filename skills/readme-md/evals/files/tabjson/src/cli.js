#!/usr/bin/env node
// tabjson: convert CSV or TSV to JSON.
// Usage: tabjson <file> [--delimiter <char>] [--pretty] [--out <file>]

import { readFileSync, writeFileSync } from "node:fs";

const args = process.argv.slice(2);
const file = args.find((a) => !a.startsWith("--"));
const flag = (name) => args.includes(`--${name}`);
const option = (name, fallback) => {
  const i = args.indexOf(`--${name}`);
  return i >= 0 ? args[i + 1] : fallback;
};

if (!file) {
  console.error("usage: tabjson <file> [--delimiter <char>] [--pretty] [--out <file>]");
  process.exit(2);
}

const delimiter = option("delimiter", file.endsWith(".tsv") ? "\t" : ",");
const [header, ...rows] = readFileSync(file, "utf8").trim().split(/\r?\n/);
const keys = header.split(delimiter);
const records = rows.map((row) =>
  Object.fromEntries(row.split(delimiter).map((value, i) => [keys[i], value])),
);
const json = JSON.stringify(records, null, flag("pretty") ? 2 : 0);

const out = option("out");
if (out) writeFileSync(out, json + "\n");
else process.stdout.write(json + "\n");
