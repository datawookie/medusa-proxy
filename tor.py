import requests

import log
import service

class Tor(service.Service):
    executable = "/usr/bin/tor"

    def __init__(self, id, new_circuit_period = None, max_circuit_dirtiness = None, circuit_build_timeout = None):
        super().__init__(10000 + id)
        self.new_circuit_period     = new_circuit_period or 120
        self.max_circuit_dirtiness  = max_circuit_dirtiness or 600
        self.circuit_build_timeout  = circuit_build_timeout or 60

        self.run(
            self.executable,
            f"--SocksPort {self.port}",
            f"--NewCircuitPeriod {self.new_circuit_period}",
            f"--MaxCircuitDirtiness {self.max_circuit_dirtiness}",
            f"--CircuitBuildTimeout {self.circuit_build_timeout}",
            f"--DataDirectory {self.data_directory}",
            f"--PidFile {self.pid_file}",
            "--Log 'info syslog'",
            '--RunAsDaemon 1',
        )
    
    @property
    def working(self):
        TEST_URL = 'http://ifconfig.me/ip'

        proxies = {
            'http': f'socks5://127.0.0.1:{self.port}',
            'https': f'socks5://127.0.0.1:{self.port}'
        }

        response = requests.get(TEST_URL, proxies=proxies)
        log.debug('Tor IP: {}'.format(response.text.strip()))

        return True

    @property
    def data_directory(self):
      return super().data_directory+"/"+str(self.port)