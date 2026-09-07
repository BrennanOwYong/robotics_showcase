import json
import os
import subprocess
import time


PID_FILE = "/tmp/ros_chat_hub.pid"
LOCK_FILE = "/tmp/ros_chat_hub.starting"
RUN_LOCK_FILE = "/tmp/ros_chat_hub.running"
READY_FILE = "/tmp/ros_chat_hub.ready"
HUB_PROCESS_NAME = "ROS CHAT HUB"
HUB_NODE_NAME = "ros_chat_hub"
BROADCAST_TOPIC = "/ros_chat/broadcast"
OUTBOUND_PREFIX = "/ros_chat/client/"
USERS_TOPIC = "/ros_chat/users"
REGISTER_SERVICE = "/ros_chat/register_user"
LEAVE_SERVICE = "/ros_chat/leave_user"
STATE_FILE = os.path.expanduser("~/.ros/ros_chat_history.json")
MAX_HISTORY = 10
HEARTBEAT_TIMEOUT = 8.0
COLORS = ["red", "green", "yellow", "blue", "magenta", "cyan", "white"]


def message_json(kind, **fields):
    payload = {"kind": kind, "timestamp": time.time()}
    payload.update(fields)
    return json.dumps(payload, separators=(",", ":"))


def outbound_topic(user_id):
    return OUTBOUND_PREFIX + user_id.replace("/", "_").replace("-", "_")


def read_hub_pid():
    try:
        with open(PID_FILE, "r", encoding="utf-8") as stream:
            pid = int(stream.read().strip())
        os.kill(pid, 0)
        with open("/proc/{}/comm".format(pid), "r", encoding="utf-8") as stream:
            process_name = stream.read().strip()
        if process_name != HUB_PROCESS_NAME:
            return None
        return pid
    except (OSError, ValueError):
        return None


def find_processes_by_name(process_name=HUB_PROCESS_NAME):
    """Return live PIDs whose Linux process name matches exactly."""
    found = []
    try:
        process_ids = os.listdir("/proc")
    except OSError:
        return found
    for entry in process_ids:
        if not entry.isdigit():
            continue
        try:
            with open("/proc/{}/comm".format(entry), "r", encoding="utf-8") as stream:
                if stream.read().strip() == process_name:
                    found.append(int(entry))
        except (OSError, UnicodeError):
            continue
    return found


def hub_is_visible(node):
    """Find the hub by process name, then confirm its ROS 2 service."""
    # The PID file is the fast path. The process-name scan is the fallback
    # during the short interval before the hub writes that file.
    if read_hub_pid() is None and not find_processes_by_name():
        return False
    return any(name == REGISTER_SERVICE
               for name, _types in node.get_service_names_and_types())


def start_hub_if_missing(node, timeout=10.0):
    """Find a ready hub or start one, then wait for ROS 2 discovery."""
    import rclpy

    # Give this new node one discovery cycle before making a decision. A live
    # hub can already exist while this node's graph cache is still empty.
    rclpy.spin_once(node, timeout_sec=0.1)
    if hub_is_visible(node):
        return True

    # Do not start a second hub. Wait for the existing process to advertise
    # its service instead.
    if find_processes_by_name():
        return wait_for_hub(node, timeout)

    child = None
    try:
        fd = os.open(LOCK_FILE, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.close(fd)
    except FileExistsError:
        pass
    else:
        child = subprocess.Popen(
            ["ros2", "run", "ros_chat", "start_node"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )

    result = wait_for_hub(node, timeout, child)
    try:
        os.unlink(LOCK_FILE)
    except FileNotFoundError:
        pass
    return result


def wait_for_hub(node, timeout=10.0, child=None):
    """Wait for the hub readiness signal and ROS service discovery."""
    import rclpy

    deadline = time.time() + timeout
    while time.time() < deadline:
        rclpy.spin_once(node, timeout_sec=0.1)
        ready_signal = os.path.exists(READY_FILE)
        if hub_is_visible(node) and (child is None or ready_signal):
            return True
        if child is not None and child.poll() is not None:
            return False
        time.sleep(0.05)
    return False


def ansi(color):
    codes = {name: code for name, code in zip(COLORS, [31, 32, 33, 34, 35, 36, 37])}
    return "\033[{}m".format(codes.get(color, 37))
