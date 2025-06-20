import json
import jinja2
import requests
from signal import SIGHUP
from pathlib import Path
import os

from . import log
from .service import Service

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

        with open("templates/tor.cfg", "rt") as file:
            template = jinja2.Template(file.read())

        # Additional parameters for bridge enable
        #
        EXITNODES = os.environ.get("TOR_EXIT_NODES", "")
        
        if EXITNODES != "":
            exitnodes_list = [x.strip().strip("'") for x in EXITNODES.split(",")]
            exitnodes_string = "{"+"},{".join(exitnodes_list) + "}"      
        else:
            exitnodes_string = ""

        BRIDGES = os.environ.get("TOR_BRIDGES", "")
        bridges_file = Path("bridges.lst")

        if bridges_file.exists():
            USEBRIDGES = "1"
            with open("bridges.lst", "r") as file_bridges:
                bridges_string = file_bridges.read()
        else:
            if BRIDGES == "":
                USEBRIDGES = "0"
                bridges_string = ""
            else:
                USEBRIDGES = "1"
                BRIDGESLIST = [x.strip().strip("'") for x in BRIDGES.split(",")]
                bridges_string = "\n".join(BRIDGESLIST) + "\n"

        config = template.render(
            new_circuit_period=self.new_circuit_period,
            new_exit_nodes=exitnodes_string,
            use_bridges=USEBRIDGES,
            bridges=bridges_string,
        )

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

        log.info(f"port {self.port}: {ip:>15} | PID {self.pid:>4}" + location)

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
