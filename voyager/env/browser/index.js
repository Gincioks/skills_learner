const express = require("express");
const puppeteer = require("puppeteer");
const fs = require("fs");
const path = require("path");
const { exec } = require("child_process");

let page;
let browser;
let eventsCache = [];

async function recordEvent(log, error) {
  const workspace = fs.readdirSync(path.join(__dirname, "./workspace"));
  const event = {
    log,
    workspace,
    currentUrl: page.url(),
    error,
  };

  // console.log(event);

  eventsCache.push(event);
}

async function init() {
  browser = await puppeteer.launch({
    headless: false,
    args: ["--lang=en-US,en"],
  });
  page = await browser.newPage();
  // await page.setDefaultNavigationTimeout(0);
  await page.goto("https://www.google.com");
}

init();

const app = express();

app.use(express.json());

app.post("/execute", async (req, res) => {
  try {
    const { code, programs } = req.body;
    if (code && programs) {
      const refactoredCode = `${programs.replace(
        /(\r\n|\n|\r)/gm,
        ""
      )};(async () => {${code}})()`;
      const eg = await eval(refactoredCode);
      console.log(eg, "eg");
    }
    await recordEvent("observe");
  } catch (e) {
    console.log(e.message);
    await recordEvent("error", e.message);
  }

  res.json({ events: eventsCache });
  fs.writeFileSync(
    path.join(__dirname, "./workspace/events.json"),
    JSON.stringify(eventsCache, null, 2)
  );
  // eventsCache = [];
});

app.listen(3000, () => console.log("Server listening on port 3000"));
