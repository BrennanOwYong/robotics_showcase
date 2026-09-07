# Portfolio structure

The repository is organised as one portfolio with five technical project areas. The original source layouts remain close to their ROS 2 package boundaries so that package manifests and launch files stay usable.

## Why this structure

Robotics projects are easier to evaluate when the problem statement, system boundary, source location, and operating notes are visible together. The root README provides the map. The Pages site provides the narrative. The source folders provide the implementation.

## What is tracked

- ROS 2 package source, launch files, configuration, interfaces, and technical notes.
- Portfolio pages and the Pages deployment workflow.
- Existing project READMEs where they provide setup or architecture information.

## What is not tracked

- ROS 2 `build/`, `install/`, and `log/` output.
- Python bytecode, test caches, and local tooling state.
- The local 147 MB demo video. GitHub rejects files larger than 100 MB. The source and written walkthrough remain available in the repository.
- Local investigation context that contains machine paths or source-repository references.
