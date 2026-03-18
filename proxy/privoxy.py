import jinja2

from .service import Service
from .haproxy import Haproxy
from .tor import Tor
from . import log


class Privoxy(Service):
    executable = "/usr/sbin/privoxy"

    def __init__(self, ntor, id=0, port=8888):
        self.id = id
        super().__init__(port + self.id)

        self.config = f"/etc/privoxy/config-{self.id}"
        self.haproxy = Haproxy(self.id, [Tor() for i in range(ntor)])

        with open("templates/privoxy.cfg", "rt") as file:
            template = jinja2.Template(file.read())

        config = template.render(
            port=self.port,
            socks=self.haproxy,
        )

        with open(self.config, "wt") as file:
            file.write(config)

        self.run(
            self.executable,
            self.config,
        )

    def rotate_circuits(self):
        """
        Rotate Tor circuits for all backend proxies.

        This sends SIGHUP to each Tor process, causing them to build new circuits
        with different exit nodes. Used for changing IP addresses periodically.
        """
        log.info(
            f"Privoxy {self.id}: Rotating {len(self.haproxy.proxies)} Tor circuits."
        )
        for tor_proxy in self.haproxy.proxies:
            tor_proxy.rotate_circuit()

    def stop(self):
        self.haproxy.stop()
