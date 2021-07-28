import os
import jinja2

import log
import service

CONFIG_PATH = "/etc/privoxy/config"

class Privoxy(service.Service):
    executable = "/usr/sbin/privoxy"

    def __init__(self, socks, port=8888):
        super().__init__(port)

        with open("templates/privoxy.cfg", "rt") as file:
            template = jinja2.Template(file.read())

        config = template.render(
            port        = self.port,
            socks       = socks,
        )

        with open(CONFIG_PATH, "wt") as file:
            file.write(config)

        self.run(
            self.executable,
            CONFIG_PATH,
        )