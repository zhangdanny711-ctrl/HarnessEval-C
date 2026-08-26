"use strict";

const fs = require("fs");
const {chromium} = require("playwright");

async function executeStep(page, origin, step) {
  if (step.kind === "goto") {
    await page.goto(origin + step.url, {waitUntil: "networkidle"});
    return {passed: true, detail: {pathname: new URL(page.url()).pathname}};
  }
  if (step.kind === "fill") {
    await page.locator(step.selector).fill(step.value);
    return {passed: true, detail: {selector: step.selector}};
  }
  if (step.kind === "click") {
    await page.locator(step.selector).click();
    return {passed: true, detail: {selector: step.selector}};
  }
  if (step.kind === "expect_text") {
    await page.waitForFunction(
      ({selector, text}) => document.querySelector(selector)?.textContent.includes(text),
      {selector: step.selector, text: step.text}
    );
    return {passed: true, detail: {selector: step.selector, expected_text: step.text}};
  }
  if (step.kind === "expect_visible") {
    await page.locator(step.selector).waitFor({state: "visible"});
    return {passed: true, detail: {selector: step.selector}};
  }
  throw new Error(`unsupported browser step: ${step.kind}`);
}

async function main() {
  const [origin, preregistrationPath] = process.argv.slice(2);
  if (!origin || !preregistrationPath) {
    throw new Error("usage: node browser_check.cjs ORIGIN PREREGISTRATION_JSON");
  }
  const preregistration = JSON.parse(fs.readFileSync(preregistrationPath, "utf8"));
  const frozenJourneys = preregistration.components.browser_flow.journeys;
  const browser = await chromium.launch({channel: process.env.PLAYWRIGHT_CHANNEL || "chrome", headless: true});
  const page = await browser.newPage();
  const journeys = [];
  try {
    for (const journey of frozenJourneys) {
      const steps = [];
      for (const frozenStep of journey.steps) {
        try {
          const observed = await executeStep(page, origin, frozenStep);
          steps.push({...frozenStep, ...observed});
        } catch (error) {
          steps.push({...frozenStep, passed: false, detail: {error_type: error.name}});
        }
      }
      journeys.push({journey_id: journey.journey_id, steps});
    }
  } finally {
    await browser.close();
  }
  process.stdout.write(JSON.stringify({journeys}));
}

main().catch(error => {
  process.stderr.write(`${error.name}: browser infrastructure failed\n`);
  process.exit(2);
});
