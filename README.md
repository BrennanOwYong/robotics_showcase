# Task 1: Swarm Communication Network Architecture

## Task 2: Refined ROS2 Telemetry and CPU Resource Allocation

> A technical portfolio of two independent ROS2 systems.

[![Open the interactive portfolio](https://img.shields.io/badge/portfolio-open%20GitHub%20Pages-0c7168?style=flat-square)](https://brennanowyong.github.io/robotics_showcase/)
[![ROS 2](https://img.shields.io/badge/ROS%202-Jazzy-22313f?style=flat-square)](https://www.ros.org/)

Open the [interactive GitHub Pages portfolio](https://brennanowyong.github.io/robotics_showcase/) for the animated Task 1 architecture and Task 2 telemetry walkthrough. This README is the technical summary.

## What was built

Task 1 is a ROS 2 swarm communication network architecture. Each terminal runs one ROS 2 client. One background hub owns registration, identity, routing, persistence, and shared system state.

Task 2 is a separate ROS2 telemetry and CPU resource allocation project. It addresses how telemetry is represented, refined, and scheduled as a runtime workload. It is documented independently from the Task 1 swarm communication network.

## Task 1 architecture

```text
client A ── /ros_chat/client/user-1 ──┐
client B ── /ros_chat/client/user-2 ──┼──► ROS CHAT HUB
client C ── /ros_chat/client/user-3 ──┘       │
                                             ├── /ros_chat/broadcast
                                             ├── /ros_chat/users
                                             └── ~/.ros/ros_chat_history.json
```

Services handle short control operations:

- `/ros_chat/register_user`
- `/ros_chat/leave_user`

Topics handle continuous records:

- `/ros_chat/client/<user-id>`: chat, heartbeat, and telemetry from one client.
- `/ros_chat/broadcast`: one validated record delivered to every client.
- `/ros_chat/users`: active-user state.

## Task 1 key design decisions

| Decision | Reason |
| --- | --- |
| Hub-and-spoke topology | One validation point and one consistent shared view. |
| One outbound topic per client | The hub can identify the topic owner and isolate client streams. |
| Shared broadcast topic | DDS distributes one validated record to every subscriber. |
| Services for registration and departure | Both operations need a direct response. |
| Topics for chat and telemetry | Both are continuous streams of records. |
| Process check followed by ROS service discovery | A Linux process can exist before its ROS 2 service is ready. |
| Ten-record display history | The terminal stays readable while retaining recent context. |
| JSON telemetry records | The message is easy to inspect, log, and extend. |

## Task 2 scope

```json
{
  "kind": "telemetry",
  "user_id": "user-2",
  "code": "FORMATION_LOST",
  "text": "Robot left formation"
}
```

Task 2 uses the telemetry record as the basis for refined runtime handling and CPU resource allocation. It is shown as a separate project in the portfolio.

The current Task 2 architecture has three boundaries:

1. A client detects a robot-state change and publishes a structured record on `/ros_chat/client/<user-id>`.
2. The hub validates the sender, adds the canonical event fields, and publishes the record on `/ros_chat/broadcast`.
3. Each client receives the same event. Telemetry processing is treated as a named workload so CPU allocation can protect robot-control work and defer presentation work when required.

The key deltas are explicit message semantics, hub-owned validation, fleet-wide broadcast visibility, and a separate runtime resource-allocation boundary. The interactive [Task 2 page](site/telemetry.html) shows the current architecture and switches between the architecture and delta views.

## Source and setup

The Task 1 package source is under [`ros2_ws/src/ros_chat/`](ros2_ws/src/ros_chat/). The Task 1 design notes are under [`ros2_ws/docs/`](ros2_ws/docs/). Task 2 is documented separately on its [project page](site/telemetry.html).

To use the package in a separate ROS 2 Jazzy workspace:

```bash
source /opt/ros/jazzy/setup.bash
mkdir -p ~/ros2_ws/src
cp -r /path/to/robotics_showcase/ros2_ws/src/ros_chat ~/ros2_ws/src/
cd ~/ros2_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --merge-install --symlink-install
source install/setup.bash
ros2 run ros_chat chat_client.py
```

Start the command in three terminals for Task 1. The first client starts the hub. Later clients register with it.

## Verification

```bash
node scripts/verify_showcase.mjs
```

The check validates the README, interactive landing page, Task 1 page, Task 2 telemetry page, shared CSS, deployment workflow, and generated-output rules.

## License

Licensing follows the package files. New portfolio documentation and site files use the MIT License.
