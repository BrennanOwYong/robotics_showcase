# Robotics Showcase

> A technical portfolio of robotics systems across control, simulation, perception, communication, and autonomous mission execution.

[![Open the visual portfolio](https://img.shields.io/badge/portfolio-open%20GitHub%20Pages-0c7168?style=flat-square)](https://brennanowyong.github.io/robotics_showcase/)
[![ROS 2](https://img.shields.io/badge/ROS%202-projects-22313f?style=flat-square)](https://www.ros.org/)
[![Language](https://img.shields.io/badge/code-Python%20%7C%20C%2B%2B-f2b84b?style=flat-square)](https://github.com/BrennanOwYong/robotics_showcase)

The [GitHub Pages site](https://brennanowyong.github.io/robotics_showcase/) is the visual presentation of the work. This README is the technical index: it identifies the problem each system addresses, the engineering approach, the implementation location, and the robotics capability it demonstrates.

## Portfolio at a glance

| System | Problem addressed | Engineering capability | Implementation |
| --- | --- | --- | --- |
| [2D PID Motion Controller](site/projects/pid-controller.html) | Move a simulated vehicle toward depth and horizontal setpoints under actuator limits. | Feedback control, discrete-time updates, bias compensation, saturation. | [`HornetXi-assignment2/`](HornetXi-assignment2/) |
| [ROS 2 Group Chat](site/projects/ros-chat.html) | Share operator messages and telemetry across independent ROS 2 processes. | Topic/service design, discovery, identity, lifecycle, persistence. | [`ros2_ws/src/ros_chat/`](ros2_ws/src/ros_chat/) |
| [BlueROV2 Simulation](site/projects/bluerov-simulation.html) | Test underwater-vehicle software without depending on physical hardware. | Gazebo integration, ArduSub SITL, MAVROS, TF, odometry, launch composition. | [`ardusub_sim/`](ardusub_sim/) |
| [YOLO/TensorRT Perception](site/projects/perception.html) | Turn camera frames into structured detections and stable tracks. | ROS 2 lifecycle management, model inference, message conversion, tracking. | [`bluerov_ws/src/yolo_ros_trt/`](bluerov_ws/src/yolo_ros_trt/) |
| [Mission Execution and Debugging](site/projects/mission-debug.html) | Make autonomous mission decisions, retries, and fallbacks understandable. | Behaviour trees, ROS 2 actions, failure handling, causal observability. | [`mission_debug/`](mission_debug/) |

## What this portfolio demonstrates

### Control

The PID controller closes the loop between a setpoint and measured vehicle state. It runs two control channels, adds a depth bias for simulated buoyancy, and clamps both thrust outputs to the simulator's `-4` to `4` range. This shows how a mathematical controller is adapted for a real system constraint.

### Communication

The ROS 2 chat system separates short control requests from streaming data. Services handle registration and departure. Per-client topics carry outbound records. A shared broadcast topic distributes validated messages, system events, and telemetry. The hub owns user identity and message history.

### Simulation and integration

The BlueROV2 stack connects ROS 2 commands to Gazebo physics through MAVROS and ArduSub SITL. The launch configuration keeps world selection, GUI mode, vehicle startup, odometry, and simulation time explicit. The package documents the interface between the simulated vehicle and downstream autonomy code.

### Perception

The YOLO node uses ROS 2 lifecycle transitions to own model setup, activation, subscription, inference, publication, and cleanup. It publishes structured detections and visual annotations. The tracking node reuses the detector and adds persistent ByteTrack state rather than duplicating the pipeline.

### Mission execution

The mission work examines how behaviour-tree sequences, selectors, retries, action feedback, and fallback paths compose an autonomous underwater task. The central design goal is explainability: stage identity, retry attempts, branch decisions, action correlation, and fallback reasons should be visible in the runtime record.

## System view

The projects form a useful robotics development chain:

```text
camera and vehicle state
          │
          ▼
perception ──► mission decision ──► control command
     │                │                    │
     └──── debug ◄────┴──── ROS 2 ◄────────┘
                          │
                          ▼
                   simulation / vehicle
```

The common design principles are explicit interfaces, tunable parameters, bounded outputs, clear ownership, and evidence that can be inspected after a run.

## Repository layout

```text
.
├── site/                         # GitHub Pages portfolio
├── docs/                         # Portfolio-level technical notes
├── HornetXi-assignment2/         # 2D PID controller and simulator
├── ros2_ws/src/ros_chat/         # ROS 2 hub-and-spoke communication system
├── ardusub_sim/                  # BlueROV2 Gazebo and ArduSub simulation
├── bluerov_ws/src/yolo_ros_trt/  # YOLO detection and tracking nodes
└── mission_debug/                # Mission execution and observability notes
```

## Running the source

Each ROS 2 package keeps its own manifest and package-level setup notes. The main simulation setup is documented in [`ardusub_sim/README.md`](ardusub_sim/README.md). The ROS 2 chat design is documented in [`ros2_ws/docs/architecture.md`](ros2_ws/docs/architecture.md). The PID package has a short run guide in [`HornetXi-assignment2/README.md`](HornetXi-assignment2/README.md).

Typical ROS 2 workflow:

```bash
source /opt/ros/<distribution>/setup.bash
cd <workspace>
colcon build --symlink-install
source install/setup.bash
```

The repository does not track generated `build/`, `install/`, or `log/` folders. Recreate them in the target ROS 2 environment.

## Verification

The portfolio structure can be checked without installing ROS 2:

```bash
node scripts/verify_showcase.mjs
```

The check validates the README, Pages entry points, project pages, shared styling, deployment workflow, and generated-output ignore rules.

## More detail

For the design narrative, diagrams, and project-by-project walkthroughs, open the [GitHub Pages portfolio](https://brennanowyong.github.io/robotics_showcase/).

## License

Licensing follows the individual package files. New portfolio documentation and site files are released under the MIT License.
