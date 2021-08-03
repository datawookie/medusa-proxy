import os
from proxy import log
import jinja2

from .service import Service

CONFIG_PATH = "/etc/haproxy/haproxy.cfg"

class Haproxy(Service):
    executable = "/usr/sbin/haproxy"

    def __init__(self, proxies, port=1080):
        super().__init__(port)
        self.proxies = proxies
        self.options = "-V"

        for proxy in proxies:
            log.debug(f"Linking proxy at port {proxy.port}.")

        with open("templates/haproxy.cfg", "rt") as file:
            template = jinja2.Template(file.read())

        config = template.render(
            pid_file    = self.pid_file,
            login       = os.environ.get("HAPROXY_LOGIN", "admin"),
            password    = os.environ.get("HAPROXY_PASSWORD", "admin"),
            port        = self.port,
            proxies     = self.proxies
        )

        with open(CONFIG_PATH, "wt") as file:
            file.write(config)

        self.run(
            self.executable,
            self.options,
            f"-f {CONFIG_PATH}",
        )
    
    def reload(self):
        self.run(
            self.executable,
            self.options,
            f"-f {CONFIG_PATH}",
            f"-p {self.pid_file}",
            f"-sf {self.pid}"
        )