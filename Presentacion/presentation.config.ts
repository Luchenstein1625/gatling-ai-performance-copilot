import changelog from "./CHANGELOG.md?raw";

const VERSION_FALLBACK = "0.0.0";
const UPDATED_AT_FALLBACK = "1970-01-01";

function parseLatestRelease(text: string): { version: string; updatedAt: string } {
  const headingWithDate = text.match(/^## \[(\d+\.\d+\.\d+)\]\s*[—-]\s*(\d{4}-\d{2}-\d{2})/m);
  if (headingWithDate) {
    return {
      version: headingWithDate[1],
      updatedAt: headingWithDate[2],
    };
  }

  const headingOnly = text.match(/^## \[(\d+\.\d+\.\d+)\]/m);
  if (headingOnly) {
    return {
      version: headingOnly[1],
      updatedAt: UPDATED_AT_FALLBACK,
    };
  }

  return {
    version: VERSION_FALLBACK,
    updatedAt: UPDATED_AT_FALLBACK,
  };
}

const latestRelease = parseLatestRelease(changelog);

export const PRESENTATION = {
  name: "Performance Intelligence Copilot",
  version: latestRelease.version,
  updatedAt: latestRelease.updatedAt,
  slideCount: 13,
} as const;
