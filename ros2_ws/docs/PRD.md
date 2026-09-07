
# Product Requirements Document: ROS 2 Group Chat

## Product goal

Provide a small group chat for three or more terminals on Ubuntu 24.04 with ROS 2 Jazzy as the middleware.

## Users

- A terminal operator is one chat user.
- The first terminal starts the hub if no hub process exists.
- Later terminals join the existing hub.

## Functional requirements

| ID | Requirement | Acceptance condition |
| --- | --- | --- |
| FR-01 | Use ROS 2 Jazzy | The package builds in an Ubuntu 24.04 ROS 2 Jazzy workspace. |
| FR-02 | Start a hub automatically | A client starts the internal `start_node` launcher when no `ROS CHAT HUB` process exists. |
| FR-03 | Run the hub in the background | The hub is a separate long-running Linux process. Closing the startup call does not stop it. |
| FR-04 | Find the hub by process name | The client scans `/proc/*/comm` for the exact name `ROS CHAT HUB`. |
| FR-05 | Confirm ROS connection | The client discovers `/ros_chat/register_user` before registration. |
| FR-06 | Assign user identity | The hub assigns a persistent running ID such as `user-1`. |
| FR-07 | Assign text colour | The hub assigns a colour to every user ID. |
| FR-08 | Send group messages | A client publishes JSON text to its own `/ros_chat/client/<user-id>` topic. |
| FR-09 | Broadcast group messages | The hub publishes one validated record to `/ros_chat/broadcast`, and every client subscribes to it. |
| FR-10 | Render colours | Own messages are white. Remote messages use the hub-assigned colour. |
| FR-11 | Show join events | All connected clients receive a system message on `/ros_chat/broadcast` when a user joins. |
| FR-12 | Show leave events | All remaining clients receive a system message on `/ros_chat/broadcast` when a user leaves. |
| FR-13 | Broadcast telemetry | A client can publish a telemetry record on its own outbound topic, and the hub broadcasts it to all clients. |
| FR-14 | Remove users on Ctrl-C | The client calls `/ros_chat/leave_user` before shutdown. |
| FR-15 | Recover from force-kill | The hub removes users after heartbeat timeout. | --> cancelled, heartbeat no longer used.
| FR-16 | Stop an empty hub | The hub exits after the last user leaves. |
| FR-17 | Persist chat data | The hub stores the latest 10 messages and the next user number in `~/.ros/ros_chat_history.json`. |

## Non-functional requirements

- Use standard ROS 2 package layout under a workspace `src` directory.
- Use ROS 2 topics for streaming data.
- Use ROS 2 services for short registration and departure requests.
- Do not use a fixed PID as a network address.
- Keep the chat usable from normal Linux terminals.
- A force-killed client must not leave a permanent active user.

## Out of scope

- Authentication and encryption.
- Multiple hubs in one ROS 2 domain.
- Cross-domain chat bridging.
- Guaranteed cleanup after `SIGKILL` without heartbeat delay.

## Technical interfaces

- `/ros_chat/client/<user-id>`: `std_msgs/msg/String`, one client to the hub. Carries chat, heartbeat, and telemetry records.
- `/ros_chat/broadcast`: `std_msgs/msg/String`, hub to every connected client.
- `/ros_chat/users`: `std_msgs/msg/String`, active user list.
- `/ros_chat/register_user`: `ros_chat/srv/RegisterUser`.
- `/ros_chat/leave_user`: `ros_chat/srv/LeaveUser`.
