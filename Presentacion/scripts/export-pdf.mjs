import playwright from "playwright";
import { copyFile, readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const { chromium } = playwright;

function getLatestVersionFromChangelog(changelogText) {
  const withDate = changelogText.match(/^## \[(\d+\.\d+\.\d+)\]\s*[—-]\s*\d{4}-\d{2}-\d{2}/m);
  if (withDate) return withDate[1];

  const withoutDate = changelogText.match(/^## \[(\d+\.\d+\.\d+)\]/m);
  if (withoutDate) return withoutDate[1];

  throw new Error("No se pudo leer la versión desde CHANGELOG.md");
}

const scriptDir = dirname(fileURLToPath(import.meta.url));
const changelogPath = resolve(scriptDir, "../CHANGELOG.md");
const changelogText = await readFile(changelogPath, "utf8");

const url = process.env.PRESENTATION_URL || "http://127.0.0.1:5173/?print=1";
const version = getLatestVersionFromChangelog(changelogText);
const output = new URL(`../public/Performance-Intelligence-Copilot-v${version}.pdf`, import.meta.url).pathname;
const latestOutput = new URL("../public/Performance-Intelligence-Copilot-latest.pdf", import.meta.url).pathname;

const browser = await chromium.launch({ headless: true });
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
