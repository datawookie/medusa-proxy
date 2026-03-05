import json
from signal import SIGHUP

import requests

from . import log
from .service import Service
from .torrc import MANAGED_TORRC_DIRECTIVES, mask_torrc_line, render_torrc_config

CONFIG_PATH = "/etc/tor/torrc"

# Number of seconds to wait when checking if a proxy is working.
#
WORKING_TIMEOUT = 5

class Tor(Service):
    executable = "/usr/bin/tor"
    count = 0

    def __init__(
        self,
        new_circuit_period=None,
        max_circuit_dirtiness=None,
        circuit_build_timeout=None,
    ):
        self.id = Tor.count
        Tor.count += 1

        super().__init__(10000 + self.id)

        self.new_circuit_period = new_circuit_period or 120
        self.max_circuit_dirtiness = max_circuit_dirtiness or 600
        self.circuit_build_timeout = circuit_build_timeout or 60

        try:
            config, extra_torrc_lines = render_torrc_config(
                new_circuit_period=self.new_circuit_period,
                max_circuit_dirtiness=self.max_circuit_dirtiness,
                circuit_build_timeout=self.circuit_build_timeout,
            )
        except ValueError as error:
            raise ValueError(f"Invalid TORRC_* configuration: {error}") from error

        for line in extra_torrc_lines:
            directive = line.split(" ", maxsplit=1)[0]
            if directive in MANAGED_TORRC_DIRECTIVES:
                log.warning(f"TORRC passthrough overrides managed directive: {directive}.")
            log.info(f"Applying TORRC directive: {mask_torrc_line(line)}")

        with open(CONFIG_PATH, "wt") as file:
            file.write(config)

        self.start()

    @property
    def working(self):
        proxies = {
            "http": f"socks5://127.0.0.1:{self.port}",
            "https": f"socks5://127.0.0.1:{self.port}",
        }

        # Get IP.
        #
        try:
            response = requests.get(
                "https://api.ipify.org?format=json",
                proxies=proxies,
                timeout=WORKING_TIMEOUT,
            )
            ip = json.loads(response.text.strip())["ip"]
            result = True
        except (
            KeyError,
            json.decoder.JSONDecodeError,
            requests.exceptions.ConnectionError,
            requests.exceptions.ReadTimeout,
        ):
            ip = "---"
            result = False

        location = ""
        #
        if result:
            # Get IP location.
            #
            try:
                response = requests.get(
                    f"http://ip-api.com/json/{ip}",
                    proxies=proxies,
                    timeout=WORKING_TIMEOUT,
                )
                location = response.json()
            except (
                json.decoder.JSONDecodeError,
                requests.exceptions.ConnectTimeout,
                requests.exceptions.ReadTimeout,
                requests.exceptions.ConnectionError,
            ):
                log.warning("🚨 Failed to get location.")

            if location:
                location = [
                    "",
                    f"{location['country']:15}",
                    f"{location['city']:18}",
                    f"{location['lat']:+6.2f} / {location['lon']:+7.2f}",
                ]
                location = " | ".join(location)

        pid = self.pid if self.pid is not None else "----"
        log.info(f"port {self.port}: {ip:>15} | PID {pid:>4}" + location)

        return result

    @property
    def data_directory(self):
        return super().data_directory + "/" + str(self.port)

    def start(self):
        self.run(
            self.executable,
            # Suppress startup messages (before torrc is parsed).
            "--quiet",
            f"--SocksPort {self.port}",
            f"--DataDirectory {self.data_directory}",
            f"--PidFile {self.pid_file}",
        )

    def cycle(self):
        log.debug(f"Requesting new exit node (port {self.port}).")
        self.kill(SIGHUP)
