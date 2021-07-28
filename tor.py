import jinja2
import requests

import log
import service

CONFIG_PATH = "/etc/tor/torrc"

class Tor(service.Service):
    executable = "/usr/bin/tor"

    def __init__(self, id, new_circuit_period = None, max_circuit_dirtiness = None, circuit_build_timeout = None):
        super().__init__(10000 + id)
        self.new_circuit_period     = new_circuit_period or 120
        self.max_circuit_dirtiness  = max_circuit_dirtiness or 600
        self.circuit_build_timeout  = circuit_build_timeout or 60

        with open("templates/tor.cfg", "rt") as file:
            template = jinja2.Template(file.read())

        config = template.render()

        with open(CONFIG_PATH, "wt") as file:
            file.write(config)

        self.start()
    
    @property
    def working(self):
        TEST_URL = 'http://ifconfig.me/ip'

        proxies = {
            'http': f'socks5://127.0.0.1:{self.port}',
            'https': f'socks5://127.0.0.1:{self.port}'
        }

        try:
            response = requests.get(TEST_URL, proxies=proxies)
            ip = response.text.strip()
            result = True
        except requests.exceptions.ConnectionError:
            ip = "---"
            result = False

        log.info(f"Testing proxy (port {self.port}): {ip}.")

        return result

    @property
    def data_directory(self):
      return super().data_directory+"/"+str(self.port)

    def start(self):
        self.run(
            self.executable,
            f"--SocksPort {self.port}",
            f"--NewCircuitPeriod {self.new_circuit_period}",
            f"--MaxCircuitDirtiness {self.max_circuit_dirtiness}",
            f"--CircuitBuildTimeout {self.circuit_build_timeout}",
            f"--DataDirectory {self.data_directory}",
            f"--PidFile {self.pid_file}",
            "--Log 'warn syslog'",
            '--RunAsDaemon 1',
        )