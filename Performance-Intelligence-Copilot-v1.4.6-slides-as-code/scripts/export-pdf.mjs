import playwright from "playwright";
import serverlessChromium from "@sparticuz/chromium";
import { copyFile } from "node:fs/promises";

const { chromium } = playwright;

const url = process.env.PRESENTATION_URL || "http://127.0.0.1:5173/?print=1";
const version = "1.5.0";
const output = new URL(`../public/Performance-Intelligence-Copilot-v${version}.pdf`, import.meta.url).pathname;
const latestOutput = new URL("../public/Performance-Intelligence-Copilot-latest.pdf", import.meta.url).pathname;

const browser = await chromium.launch({
  args: serverlessChromium.args,
  executablePath: await serverlessChromium.executablePath(),
  headless: true,
});
const page = await browser.newPage({ viewport: { width: 1600, height: 900 } });
await page.goto(url, { waitUntil: "networkidle" });
await page.waitForSelector(".print-deck .slide");
await page.emulateMedia({ media: "print" });
await page.pdf({
  path: output,
  width: "13.333in",
  height: "7.5in",
  printBackground: true,
  preferCSSPageSize: true,
  margin: { top: "0", right: "0", bottom: "0", left: "0" },
});
await browser.close();
await copyFile(output, latestOutput);

console.log(`${output}\n${latestOutput}`);
