import { existsSync, readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";

const root = process.cwd();
const requiredFiles = [
  "README.md",
  "site/index.html",
  "site/styles.css",
  "site/app.js",
  "site/projects/pid-controller.html",
  "site/projects/ros-chat.html",
  "site/projects/bluerov-simulation.html",
  "site/projects/perception.html",
  "site/projects/mission-debug.html",
  ".github/workflows/pages.yml",
];

for (const file of requiredFiles) {
  if (!existsSync(join(root, file))) throw new Error(`Missing ${file}`);
}

const readme = readFileSync(join(root, "README.md"), "utf8");
if (!readme.includes("Robotics Showcase") || !readme.includes("GitHub Pages site")) {
  throw new Error("README does not contain the technical portfolio introduction and site link");
}

for (const file of requiredFiles.filter((item) => item.startsWith("site/") && item !== "site/styles.css")) {
  const content = readFileSync(join(root, file), "utf8");
  if (!content.includes("styles.css")) throw new Error(`${file} does not load the shared stylesheet`);
}
if (!readFileSync(join(root, "site/index.html"), "utf8").includes("app.js")) {
  throw new Error("Landing page does not load the interaction script");
}

const pageFiles = readdirSync(join(root, "site/projects"));
if (pageFiles.filter((file) => file.endsWith(".html")).length !== 5) {
  throw new Error("The site must contain five project pages");
}

const ignore = readFileSync(join(root, ".gitignore"), "utf8");
for (const pattern of ["**/build/", "**/install/", "**/log/", "**/__pycache__/"]) {
  if (!ignore.includes(pattern)) throw new Error(`Missing generated-output ignore rule: ${pattern}`);
}

console.log("SHOWCASE_VERIFICATION_PASSED");
