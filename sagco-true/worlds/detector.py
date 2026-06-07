"""
SAGCO World Detector
Identifies the execution environment and loads the correct world adapter.
Zero external dependencies.
"""

from __future__ import annotations
import os
import platform
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class WorldProfile:
    name: str
    shell: str
    python: str
    has_git: bool
    has_docker: bool
    has_kubectl: bool
    path_sep: str
    home: str
    extra: dict = field(default_factory=dict)


def detect() -> WorldProfile:
    name = _detect_world_name()
    return WorldProfile(
        name=name,
        shell=os.environ.get("SHELL", os.environ.get("COMSPEC", "unknown")),
        python=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        has_git=shutil.which("git") is not None,
        has_docker=shutil.which("docker") is not None,
        has_kubectl=shutil.which("kubectl") is not None,
        path_sep=os.pathsep,
        home=str(Path.home()),
        extra=_extra_for(name),
    )


def _detect_world_name() -> str:
    if os.environ.get("TERMUX_VERSION") or os.path.exists("/data/data/com.termux"):
        return "termux"
    if os.path.exists("/.dockerenv") or os.path.exists("/run/.containerenv"):
        return "docker"
    if os.environ.get("KUBERNETES_SERVICE_HOST"):
        return "kubernetes"
    if "microsoft" in platform.uname().release.lower():
        return "wsl"
    sys_name = platform.system()
    if sys_name == "Windows":
        return "windows"
    if sys_name == "Linux":
        return "linux"
    if sys_name == "Darwin":
        return "darwin"
    return "unknown"


def _extra_for(name: str) -> dict:
    extras: dict[str, Any] = {}
    if name == "termux":
        extras["termux_prefix"] = os.environ.get("PREFIX", "/data/data/com.termux/files/usr")
        extras["android_home"] = os.environ.get("HOME", "/data/data/com.termux/files/home")
    elif name == "windows":
        extras["comspec"] = os.environ.get("COMSPEC", "cmd.exe")
        extras["userprofile"] = os.environ.get("USERPROFILE", "")
        extras["programfiles"] = os.environ.get("PROGRAMFILES", "C:\\Program Files")
    elif name == "docker":
        extras["hostname"] = os.environ.get("HOSTNAME", "")
        extras["container_id"] = open("/etc/hostname").read().strip() if os.path.exists("/etc/hostname") else ""
    elif name == "kubernetes":
        extras["namespace"] = os.environ.get("KUBERNETES_NAMESPACE", "default")
        extras["service_host"] = os.environ.get("KUBERNETES_SERVICE_HOST", "")
    return extras


# ── World adapter base ────────────────────────────────────────────────────

class WorldAdapter:
    """Base adapter — defines the interface all world adapters must implement."""
    name: str = "base"

    def exec(self, command: str, capture: bool = True) -> str:
        raise NotImplementedError

    def read_env(self, key: str, default: str = "") -> str:
        return os.environ.get(key, default)

    def path_exists(self, path: str) -> bool:
        return os.path.exists(path)

    def read_file(self, path: str) -> str:
        try:
            return open(path).read()
        except Exception:
            return ""

    def write_file(self, path: str, content: str) -> bool:
        try:
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            with open(path, "w") as f:
                f.write(content)
            return True
        except Exception:
            return False


class LinuxAdapter(WorldAdapter):
    name = "linux"

    def exec(self, command: str, capture: bool = True) -> str:
        import subprocess
        result = subprocess.run(command, shell=True, capture_output=capture, text=True, timeout=30)
        return result.stdout.strip() if capture else ""


class TermuxAdapter(LinuxAdapter):
    name = "termux"


class DockerAdapter(LinuxAdapter):
    name = "docker"


class WindowsAdapter(WorldAdapter):
    name = "windows"

    def exec(self, command: str, capture: bool = True) -> str:
        import subprocess
        result = subprocess.run(
            ["powershell", "-Command", command],
            capture_output=capture, text=True, timeout=30
        )
        return result.stdout.strip() if capture else ""


class KubernetesAdapter(LinuxAdapter):
    name = "kubernetes"


_ADAPTER_MAP: dict[str, type[WorldAdapter]] = {
    "linux":      LinuxAdapter,
    "termux":     TermuxAdapter,
    "docker":     DockerAdapter,
    "wsl":        LinuxAdapter,
    "darwin":     LinuxAdapter,
    "windows":    WindowsAdapter,
    "kubernetes": KubernetesAdapter,
}


def get_adapter(world_name: str | None = None) -> WorldAdapter:
    name = world_name or _detect_world_name()
    cls = _ADAPTER_MAP.get(name, WorldAdapter)
    return cls()


if __name__ == "__main__":
    import json
    profile = detect()
    print(json.dumps({
        "name":       profile.name,
        "shell":      profile.shell,
        "python":     profile.python,
        "has_git":    profile.has_git,
        "has_docker": profile.has_docker,
        "path_sep":   profile.path_sep,
        "home":       profile.home,
        "extra":      profile.extra,
    }, indent=2))
