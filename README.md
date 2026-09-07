# ROS 2 Mission Telemetry Showcase

> A technical portfolio of a ROS 2 group communication system and its telemetry path.

[![Open the interactive portfolio](https://img.shields.io/badge/portfolio-open%20GitHub%20Pages-0c7168?style=flat-square)](https://brennanowyong.github.io/robotics_showcase/)
[![ROS 2](https://img.shields.io/badge/ROS%202-Jazzy-22313f?style=flat-square)](https://www.ros.org/)

Open the [interactive GitHub Pages portfolio](https://brennanowyong.github.io/robotics_showcase/) for the visual architecture maps and telemetry message walkthrough. This README is the technical summary.

## What was built

Task 1 is a ROS 2 hub-and-spoke group communication system. Each terminal runs one ROS 2 client. One background hub owns registration, identity, routing, persistence, and shared system state.

Telemetry extends the same transport. A client publishes a structured event on its outbound topic. The hub validates the sender and broadcasts one record to every subscribed client. This lets a robot report state changes such as formation loss to the whole system.

## Architecture

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

## Key design decisions

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

## Telemetry record

```json
{
  "kind": "telemetry",
  "user_id": "user-2",
  "code": "FORMATION_LOST",
  "text": "Robot left formation"
}
```

The shared topic provides delivery and visibility. It is not an authentication or encryption boundary.

## Source and setup

The package source is under [`ros2_ws/src/ros_chat/`](ros2_ws/src/ros_chat/). The design notes are under [`ros2_ws/docs/`](ros2_ws/docs/).

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

Start the command in three terminals. The first client starts the hub. Later clients register with it.

## Verification

```bash
node scripts/verify_showcase.mjs
```

The check validates the README, interactive landing page, Task 1 page, telemetry page, shared CSS, deployment workflow, and generated-output rules.

## License

Licensing follows the package files. New portfolio documentation and site files use the MIT License.
