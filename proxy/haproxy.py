import os
from proxy import log
import jinja2

from .service import Service


class Haproxy(Service):
    executable = "/usr/sbin/haproxy"

    def __init__(self, id, proxies, port=1080):
        self.id = id
        super().__init__(port + self.id)
        self.proxies = proxies
        self.options = "-V"
        self.config = f"/etc/haproxy/haproxy-{self.id}"

        for proxy in self.proxies:
            log.debug(f"Linking proxy at port {proxy.port}.")

        with open("templates/haproxy.cfg", "rt") as file:
            template = jinja2.Template(file.read(), keep_trailing_newline=True)

        config = template.render(
            pid_file=self.pid_file,
            login=os.environ.get("HAPROXY_LOGIN", "admin"),
            password=os.environ.get("HAPROXY_PASSWORD", "admin"),
            port=self.port,
            stats=2090 + self.id,
            proxies=self.proxies,
        )

        with open(self.config, "wt") as file:
            file.write(config)

        self.run(
            self.executable,
            self.options,
            f"-f {self.config}",
        )

    def reload(self):
        self.run(
            self.executable,
            self.options,
            f"-f {self.config}",
            f"-p {self.pid_file}",
            f"-sf {self.pid}",
        )

    def stop(self):
        for proxy in self.proxies:
            del proxy
