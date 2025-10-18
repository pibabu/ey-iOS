import docker
import os
import json
from typing import Optional, Dict, Any
from datetime import datetime
import asyncio
from pathlib import Path


class ContainerManager:
    """
    Manages Docker containers for each user with isolated environments
    and shared resources via volumes.
    """

    def __init__(self):
        """Initialize Docker client and configuration"""
        self.client = docker.from_env()
        self.network_name = "ai_platform_network"
        self.shared_volume_name = "shared_volume"
        self.container_prefix = "user_container"
        self.image_name = "ubuntu:22.04"

        # Ensure network and shared volume exist
        self._ensure_network()
        self._ensure_shared_volume()

    def _ensure_network(self):
        """Create Docker network if it doesn't exist"""
        try:
            self.client.networks.get(self.network_name)
            print(f"✓ Network '{self.network_name}' already exists")
        except docker.errors.NotFound:
            self.client.networks.create(
                self.network_name,
                driver="bridge",
                options={"com.docker.network.bridge.name": "ai_platform_br0"},
            )
            print(f"✓ Created network '{self.network_name}'")

    def _ensure_shared_volume(self):
        """Create shared volume if it doesn't exist"""
        try:
            self.client.volumes.get(self.shared_volume_name)
            print(f"✓ Shared volume '{self.shared_volume_name}' already exists")
        except docker.errors.NotFound:
            self.client.volumes.create(name=self.shared_volume_name, driver="local")
            print(f"✓ Created shared volume '{self.shared_volume_name}'")

    def create_user_container(
        self, user_id: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create and start a container for a specific user

        Args:
            user_id: Unique identifier for the user
            metadata: Optional metadata (tier, limits, etc.)

        Returns:
            Container information dictionary
        """
        container_name = f"{self.container_prefix}_{user_id}"
        user_volume_name = f"user_{user_id}_volume"

        # Check if container already exists
        existing = self.get_container(user_id)
        if existing and existing.get("status") == "running":
            return existing

        # Create user-specific volume
        try:
            self.client.volumes.get(user_volume_name)
        except docker.errors.NotFound:
            self.client.volumes.create(
                name=user_volume_name,
                driver="local",
                labels={
                    "user_id": user_id,
                    "created_at": datetime.utcnow().isoformat(),
                },
            )

        # Prepare metadata
        if metadata is None:
            metadata = {}

        metadata.update(
            {
                "user_id": user_id,
                "created_at": datetime.utcnow().isoformat(),
                "volume": user_volume_name,
            }
        )

        # Container configuration
        container_config = {
            "image": self.image_name,
            "name": container_name,
            "detach": True,
            "network": self.network_name,
            "volumes": {
                user_volume_name: {"bind": "/home/user", "mode": "rw"},
                self.shared_volume_name: {
                    "bind": "/shared",
                    "mode": "ro",  # Read-only for security
                },
            },
            "labels": metadata,
            "command": "tail -f /dev/null",  # Keep container running
            "environment": {"USER_ID": user_id, "WORKSPACE": "/home/user"},
            # Resource limits
            "mem_limit": metadata.get("memory_limit", "512m"),
            "cpu_period": 100000,
            "cpu_quota": int(metadata.get("cpu_quota", 0.5) * 100000),
            # Security
            "cap_drop": ["ALL"],
            "cap_add": ["CHOWN", "DAC_OVERRIDE", "FOWNER", "SETGID", "SETUID"],
            "security_opt": ["no-new-privileges:true"],
        }

        try:
            # Remove old container if exists
            try:
                old_container = self.client.containers.get(container_name)
                old_container.remove(force=True)
            except docker.errors.NotFound:
                pass

            # Create and start container
            container = self.client.containers.run(**container_config)

            # Initialize user environment
            self._initialize_user_environment(container, user_id)

            return {
                "container_id": container.id,
                "container_name": container_name,
                "user_id": user_id,
                "status": "running",
                "volume": user_volume_name,
                "network": self.network_name,
                "created_at": metadata["created_at"],
            }

        except Exception as e:
            print(f"❌ Error creating container for user {user_id}: {e}")
            raise

    def _initialize_user_environment(self, container, user_id: str):
        """Initialize the user's home directory structure"""
        init_commands = [
            "mkdir -p /home/user/projects",
            "mkdir -p /home/user/data",
            "mkdir -p /home/user/.config",
            f"echo 'Welcome to your AI workspace, user {user_id}!' > /home/user/README.md",
            "echo '# Your Projects' > /home/user/projects/README.md",
            "chmod -R 755 /home/user",
        ]

        for cmd in init_commands:
            container.exec_run(cmd, user="root")

    def get_container(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get container information for a user"""
        container_name = f"{self.container_prefix}_{user_id}"

        try:
            container = self.client.containers.get(container_name)
            return {
                "container_id": container.id,
                "container_name": container_name,
                "user_id": user_id,
                "status": container.status,
                "volume": container.labels.get("volume"),
                "network": self.network_name,
                "created_at": container.labels.get("created_at"),
            }
        except docker.errors.NotFound:
            return None

    def stop_container(self, user_id: str) -> bool:
        """Stop a user's container"""
        container_name = f"{self.container_prefix}_{user_id}"

        try:
            container = self.client.containers.get(container_name)
            container.stop(timeout=10)
            return True
        except docker.errors.NotFound:
            return False

    def remove_container(self, user_id: str, remove_volume: bool = False) -> bool:
        """Remove a user's container and optionally their volume"""
        container_name = f"{self.container_prefix}_{user_id}"
        user_volume_name = f"user_{user_id}_volume"

        try:
            # Remove container
            container = self.client.containers.get(container_name)
            container.remove(force=True)

            # Remove volume if requested
            if remove_volume:
                try:
                    volume = self.client.volumes.get(user_volume_name)
                    volume.remove()
                except docker.errors.NotFound:
                    pass

            return True
        except docker.errors.NotFound:
            return False

    def execute_command(
        self, user_id: str, command: str, workdir: str = "/home/user"
    ) -> Dict[str, Any]:
        """
        Execute a command in user's container

        Args:
            user_id: User identifier
            command: Command to execute
            workdir: Working directory

        Returns:
            Execution result with output and exit code
        """
        container_name = f"{self.container_prefix}_{user_id}"

        try:
            container = self.client.containers.get(container_name)

            # Ensure container is running
            if container.status != "running":
                container.start()

            # Execute command
            result = container.exec_run(command, workdir=workdir, user="root")

            return {
                "exit_code": result.exit_code,
                "output": result.output.decode("utf-8"),
                "success": result.exit_code == 0,
            }

        except docker.errors.NotFound:
            raise ValueError(f"Container for user {user_id} not found")
        except Exception as e:
            raise RuntimeError(f"Command execution failed: {e}")

    def list_user_files(self, user_id: str, path: str = "/home/user") -> list:
        """List files in user's container"""
        result = self.execute_command(user_id, f"ls -la {path}")

        if result["success"]:
            return result["output"].split("\n")
        return []

    def read_user_file(self, user_id: str, file_path: str) -> str:
        """Read a file from user's container"""
        result = self.execute_command(user_id, f"cat {file_path}")

        if result["success"]:
            return result["output"]
        raise FileNotFoundError(f"File {file_path} not found or unreadable")

    def write_user_file(self, user_id: str, file_path: str, content: str) -> bool:
        """Write content to a file in user's container"""
        # Escape content for shell
        escaped_content = content.replace("'", "'\\''")

        result = self.execute_command(
            user_id, f"sh -c 'echo \"{escaped_content}\" > {file_path}'"
        )

        return result["success"]

    def get_container_stats(self, user_id: str) -> Dict[str, Any]:
        """Get resource usage statistics for a container"""
        container_name = f"{self.container_prefix}_{user_id}"

        try:
            container = self.client.containers.get(container_name)
            stats = container.stats(stream=False)

            # Calculate CPU percentage
            cpu_delta = (
                stats["cpu_stats"]["cpu_usage"]["total_usage"]
                - stats["precpu_stats"]["cpu_usage"]["total_usage"]
            )
            system_delta = (
                stats["cpu_stats"]["system_cpu_usage"]
                - stats["precpu_stats"]["system_cpu_usage"]
            )
            cpu_percent = (cpu_delta / system_delta) * 100.0 if system_delta > 0 else 0

            # Calculate memory usage
            memory_usage = stats["memory_stats"]["usage"]
            memory_limit = stats["memory_stats"]["limit"]
            memory_percent = (memory_usage / memory_limit) * 100.0

            return {
                "cpu_percent": round(cpu_percent, 2),
                "memory_usage_mb": round(memory_usage / (1024 * 1024), 2),
                "memory_limit_mb": round(memory_limit / (1024 * 1024), 2),
                "memory_percent": round(memory_percent, 2),
            }

        except docker.errors.NotFound:
            raise ValueError(f"Container for user {user_id} not found")

    def cleanup_inactive_containers(self, max_idle_hours: int = 24):
        """Remove containers that have been inactive for too long"""
        containers = self.client.containers.list(all=True)
        removed_count = 0

        for container in containers:
            if not container.name.startswith(self.container_prefix):
                continue

            # Check last activity
            created_at = container.labels.get("created_at")
            if created_at:
                created_time = datetime.fromisoformat(created_at)
                idle_hours = (datetime.utcnow() - created_time).total_seconds() / 3600

                if idle_hours > max_idle_hours and container.status != "running":
                    container.remove(force=True)
                    removed_count += 1

        return removed_count
