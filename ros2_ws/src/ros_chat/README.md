# ROS 2 Jazzy Group Chat

This package targets Ubuntu 24.04 (Noble) with ROS 2 Jazzy. ROS 2 provides the middleware. The design is hub-and-spoke:

See [the architecture decision](../../../docs/architecture.md), [the PRD](../../../docs/PRD.md), and the [definition of done](../../../docs/definition-of-done.md).

```text
terminal client A --private outbound topic--> ROS CHAT HUB --shared broadcast topic--> all clients
terminal client B --private outbound topic--> ROS CHAT HUB --shared broadcast topic--> all clients
```

## Hub election and persistence

Every client checks the hub PID and process name, then confirms the ROS 2 service `/ros_chat/register_user`. If no matching process exists, one client atomically runs the internal `scripts/start_node` launcher as a detached background process. Users do not run this launcher manually. The hub writes its current PID for inspection and sets its Linux process name to `ROS CHAT HUB`.

Later clients read the PID, find the existing hub, and use the ROS 2 `RegisterUser` service. The hub assigns the next running number (`user-1`, `user-2`, and so on) and one of seven terminal colours. The hub stores history and the next number in `~/.ros/ros_chat_history.json`.

After registration, each client publishes chat messages and heartbeats to its own outbound topic, such as `/ros_chat/client/user_1`. The hub creates a subscription for that topic. The hub validates the sender and publishes one record on `/ros_chat/broadcast`. Every client subscribes to that shared topic, including the sender. The client does not locally echo its message, so each message is rendered once. The hub includes the assigned colour in each message.

Chat, join, leave, and telemetry records use `/ros_chat/broadcast`. Each client stores them in the same ten-record CLI history and sorts them by timestamp. A client can publish a `telemetry` record on its outbound topic when it detects a robot fault or formation change. The hub broadcasts that record to all clients.

When a client receives Ctrl-C, its signal hook calls `/ros_chat/leave_user`. The hub removes that user immediately and broadcasts a system message such as `user-2 left the chat`. The hub also broadcasts join messages. If no users remain, the hub exits. If a terminal is killed forcefully, the hook cannot run; the heartbeat timeout removes that user instead.

## Build

Install ROS 2 Jazzy for Ubuntu 24.04, then source it:

```bash
source /opt/ros/jazzy/setup.bash
sudo apt install ros-jazzy-ros-base ros-jazzy-ament-cmake-python
mkdir -p ~/ros2_ws/src
cp -r /path/to/Hornet/ros2_ws/src/ros_chat ~/ros2_ws/src/
cd ~/ros2_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --merge-install --symlink-install
source install/setup.bash
```

Edit only the files under `ros2_ws/src/ros_chat`. The `build`, `install`, and `log` directories are generated output. They are not source code. On the current development container, the package-local setup also works if the top-level setup does not add the overlay:

```bash
source install/share/ros_chat/local_setup.bash
```

This package uses `ament_cmake`, not `ament_python`, because it defines the custom `RegisterUser.srv` and `LeaveUser.srv` interfaces. The normal ROS 2 Python publisher/subscriber tutorial uses `ros2 pkg create --build-type ament_python`; the equivalent command for this package type is:

```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_cmake --license MIT ros_chat
```

The repository already contains the completed package files. Use the command above only when creating a new empty package from scratch.

## Run three terminals

In each terminal, source both ROS and the workspace, then run:

```bash
ros2 run ros_chat chat_client.py
```

The first terminal starts the background hub. The second and third terminals join it. You can set an optional display name:

```bash
ros2 run ros_chat chat_client.py --name alice
```

To inspect the middleware connections:

```bash
ros2 node list
ros2 topic list
ros2 topic list | grep /ros_chat
ros2 service list | grep ros_chat
cat /tmp/ros_chat_hub.pid
ps -p "$(cat /tmp/ros_chat_hub.pid)" -o pid,comm,args
```

The hub is a separate background software process. To stop it after the demo, use the PID shown by the last command:

```bash
kill "$(cat /tmp/ros_chat_hub.pid)"
```
