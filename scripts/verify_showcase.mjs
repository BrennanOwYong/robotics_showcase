import { existsSync, readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";

const root = process.cwd();
const requiredFiles = [
  "README.md",
  "site/index.html",
  "site/styles.css",
  "site/app.js",
  "site/task1.html",
  "site/telemetry.html",
  ".github/workflows/pages.yml",
];

for (const file of requiredFiles) {
  if (!existsSync(join(root, file))) throw new Error(`Missing ${file}`);
}

const readme = readFileSync(join(root, "README.md"), "utf8");
if (!readme.includes("Swarm Communication Network Architecture") || !readme.includes("Refined ROS2 Telemetry") || !readme.includes("GitHub Pages")) {
  throw new Error("README does not contain the technical portfolio introduction and site link");
}

for (const file of requiredFiles.filter((item) => item.startsWith("site/") && item.endsWith(".html"))) {
  const content = readFileSync(join(root, file), "utf8");
  if (!content.includes("styles.css")) throw new Error(`${file} does not load the shared stylesheet`);
}
const index = readFileSync(join(root, "site/index.html"), "utf8");
const task1 = readFileSync(join(root, "site/task1.html"), "utf8");
if (!index.includes("project-pair") || !index.includes("Task 1") || !index.includes("Task 2") || !task1.includes("data-animation") || !task1.includes("data-action=\"next\"")) {
  throw new Error("Landing page does not separate the two projects or expose the Task 1 animation");
}

const pageFiles = readdirSync(join(root, "site"));
if (!pageFiles.includes("task1.html") || !pageFiles.includes("telemetry.html")) {
  throw new Error("The site must contain Task 1 and telemetry pages");
}

const ignore = readFileSync(join(root, ".gitignore"), "utf8");
for (const pattern of ["**/build/", "**/install/", "**/log/", "**/__pycache__/"]) {
  if (!ignore.includes(pattern)) throw new Error(`Missing generated-output ignore rule: ${pattern}`);
}

console.log("SHOWCASE_VERIFICATION_PASSED");
