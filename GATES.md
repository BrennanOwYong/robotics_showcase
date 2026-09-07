# Robotics showcase portfolio

OWNS: README.md, .gitignore, docs/**, site/**, scripts/**, .github/**, GATES.md

Scope: A clean, public-facing robotics portfolio repository with project documentation and a deployable GitHub Pages site.

- [x] G1: The repository has a clear public-facing README with project links and setup guidance.
  CHECK: node scripts/verify_showcase.mjs
  EXPECT: SHOWCASE_VERIFICATION_PASSED
  EVIDENCE: `node scripts/verify_showcase.mjs` passed.

- [x] G2: The site contains a working landing page and one page for each documented project.
  CHECK: node scripts/verify_showcase.mjs
  EXPECT: SHOWCASE_VERIFICATION_PASSED
  EVIDENCE: local verification passed; GitHub Pages deployment run 34129930360 passed.

- [x] G3: Generated ROS build, install, and log output is excluded from version control.
  CHECK: node scripts/verify_showcase.mjs
  EXPECT: SHOWCASE_VERIFICATION_PASSED
  EVIDENCE: `node scripts/verify_showcase.mjs` passed.

- [x] G4: The final repository is committed and pushed to the requested GitHub remote.
  EVIDENCE: `main` points to the pushed portfolio commit; Pages URL returns HTTP 200.
