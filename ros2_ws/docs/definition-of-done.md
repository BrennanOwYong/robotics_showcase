# Definition of Done

The ROS 2 group chat is done when all items below are true.

## Build

- [ ] Ubuntu 24.04 is used.
- [ ] `/opt/ros/jazzy/setup.bash` is sourced.
- [ ] `ros2 pkg list` runs successfully.
- [ ] `ros2 pkg create` has been used to establish the standard package workflow.
- [ ] `colcon build --symlink-install` completes with no errors.
- [ ] The package is located under `<workspace>/src/ros_chat`.

## Hub lifecycle

- [ ] No hub is running before the first client starts.
- [ ] The first client finds no `ROS CHAT HUB` process.
- [ ] The first client starts the internal `start_node` launcher.
- [ ] The hub remains as a separate Linux background process.
- [ ] `ps -o pid,comm,args` shows the process name `ROS CHAT HUB`.
- [ ] A later client finds the existing process by name.
- [ ] The client confirms `/ros_chat/register_user` through ROS 2 discovery.
- [ ] The last cleanly leaving user causes the hub to exit.
- [ ] A force-killed user is removed after heartbeat timeout.

## Chat behavior

- [ ] Three clients can register.
- [ ] Each client receives a unique running user ID.
- [ ] Each user ID has a hub-assigned colour.
- [ ] A message entered on terminal 1 appears on terminals 2 and 3.
- [ ] Terminal 1 displays its own message in white.
- [ ] Terminals 2 and 3 display terminal 1's message in terminal 1's assigned colour.
- [ ] A message entered on terminal 2 appears on terminals 1 and 3.
- [ ] Terminal 1 displays terminal 2's message in terminal 2's assigned colour.
- [ ] Join and leave events appear on the other active terminals.
- [ ] Only the latest 10 chat messages are displayed.
- [ ] History remains available after hub restart.

## Evidence

- [ ] Terminal screenshots or video show three active clients.
- [ ] `ros2 node list` shows the hub and client nodes.
- [ ] `ros2 topic list` shows the chat topics.
- [ ] `ros2 service list` shows registration and departure services.
- [ ] The test procedure and observed results are recorded in the submission README.
