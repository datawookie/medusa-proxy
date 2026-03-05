import os
import shutil
import subprocess

import pytest

IMAGE_TAG = "medusa-proxy:torrc-smoke"

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_CONTAINER_SMOKE") != "1",
    reason="Set RUN_CONTAINER_SMOKE=1 to run Docker smoke tests",
)


@pytest.fixture(scope="module")
def built_image_tag():
    if shutil.which("docker") is None:
        pytest.skip("docker is not installed")

    subprocess.run(["docker", "build", "-t", IMAGE_TAG, "."], check=True)
    return IMAGE_TAG


def test_generated_torrc_contains_passthrough_and_managed_values(built_image_tag):
    script = (
        "from proxy.tor import Tor; "
        "Tor.start=lambda self: None; "
        "Tor(); "
        "print(open('/etc/tor/torrc','rt').read())"
    )

    result = subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "-e",
            "TORRC_SafeLogging=1",
            "-e",
            'TORRC_EXIT_POLICY=["reject *:*","accept *:443"]',
            "-e",
            "TOR_EXIT_NODES=ru,en",
            "--entrypoint",
            "python3",
            built_image_tag,
            "-c",
            script,
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "SafeLogging 1" in result.stdout
    assert "ExitPolicy reject *:*" in result.stdout
    assert "ExitPolicy accept *:443" in result.stdout
    assert "ExitNodes {ru},{en}" in result.stdout


def test_invalid_torrc_env_fails_fast_with_actionable_error(built_image_tag):
    script = "from proxy.tor import Tor; Tor.start=lambda self: None; Tor()"
    result = subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "-e",
            "TORRC_9Bad=1",
            "--entrypoint",
            "python3",
            built_image_tag,
            "-c",
            script,
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "Invalid TORRC_* configuration" in result.stderr
