import jinja2

from .service import Service
from .haproxy import Haproxy
from .tor import Tor

CONFIG_PATH = "/etc/privoxy/config"

class Privoxy(Service):
    executable = "/usr/sbin/privoxy"

    def __init__(self, ntor, id = 0, port=8888):
        self.id = id
        super().__init__(port + self.id)

        self.haproxy = Haproxy([Tor() for i in range(ntor)])

        with open("templates/privoxy.cfg", "rt") as file:
            template = jinja2.Template(file.read())

        config = template.render(
            port        = self.port,
            socks       = self.haproxy,
        )

        with open(CONFIG_PATH, "wt") as file:
            file.write(config)

        self.run(
            self.executable,
            CONFIG_PATH,
        )

    def cycle(self):
        for proxy in self.haproxy.proxies:
            proxy.cycle()

    def stop(self):