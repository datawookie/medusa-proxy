import json
import os
import re
from pathlib import Path

import jinja2

TORRC_ENV_PREFIX = "TORRC_"
TORRC_ENV_PATTERN = re.compile(r"^TORRC_([A-Za-z][A-Za-z0-9_]*)$")
TORRC_DIRECTIVE_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9]*$")
MANAGED_TORRC_DIRECTIVES = {
    "NewCircuitPeriod",
    "MaxCircuitDirtiness",
    "CircuitBuildTimeout",
    "LearnCircuitBuildTimeout",
    "ExitNodes",
    "UseBridges",
    "ClientTransportPlugin",
}
SENSITIVE_TORRC_KEYWORDS = ("password", "secret", "token")


def _normalize_torrc_directive(token):
    parts = [part for part in token.split("_") if part]
    if not parts:
        raise ValueError(f"Invalid TORRC directive token: {token!r}.")

    normalized_parts = []
    for part in parts:
        if part.isupper():
            part = part.lower()
        normalized_parts.append(part[:1].upper() + part[1:])

    directive = "".join(normalized_parts)
    if not TORRC_DIRECTIVE_PATTERN.fullmatch(directive):
        raise ValueError(
            f"Invalid TORRC directive name {directive!r}. "
            "Expected letters and digits only (first char must be a letter)."
        )

    return directive


def _parse_torrc_values(key, raw_value):
    value = raw_value.strip()
    if not value:
        raise ValueError(f"{key!r} has an empty value; a non-empty value is required.")

    if value.startswith("["):
        try:
            parsed_values = json.loads(value)
        except json.JSONDecodeError as error:
            raise ValueError(f"{key!r} must contain valid JSON when using list syntax.") from error

        if not isinstance(parsed_values, list):
            raise ValueError(f"{key!r} JSON value must be a list of strings.")
        if not parsed_values:
            raise ValueError(f"{key!r} JSON list cannot be empty.")

        normalized_values = []
        for index, item in enumerate(parsed_values, start=1):
            if not isinstance(item, str):
                raise ValueError(f"{key!r} list item {index} must be a string.")
            normalized_item = item.strip()
            if not normalized_item:
                raise ValueError(f"{key!r} list item {index} cannot be empty.")
            if "\n" in normalized_item or "\r" in normalized_item:
                raise ValueError(f"{key!r} list item {index} must be single-line.")
            normalized_values.append((index, normalized_item))

        return normalized_values

    if "\n" in value or "\r" in value:
        raise ValueError(f"{key!r} contains a newline; use a JSON list for repeated directives.")

    return [(0, value)]


def build_torrc_passthrough_lines(env=None):
    """Build validated extra torrc lines from TORRC_* environment variables."""
    if env is None:
        env = os.environ

    entries = []
    seen_directives = {}

    for key, raw_value in env.items():
        if not key.startswith(TORRC_ENV_PREFIX):
            continue

        suffix = key[len(TORRC_ENV_PREFIX) :]
        if "__" in suffix:
            raise ValueError(
                f"Invalid environment variable {key!r}. "
                "Expected TORRC_<Directive>. Use JSON list syntax in TORRC_<Directive> for repeats."
            )

        match = TORRC_ENV_PATTERN.fullmatch(key)
        if match is None:
            raise ValueError(
                f"Invalid environment variable {key!r}. "
                "Expected TORRC_<Directive>."
            )

        (directive_token,) = match.groups()
        directive = _normalize_torrc_directive(directive_token)
        if directive in seen_directives:
            existing = seen_directives[directive]
            raise ValueError(
                f"{key!r} duplicates {existing!r} after normalization. "
                "Use only one variable per directive."
            )
        seen_directives[directive] = key

        parsed_values = _parse_torrc_values(key, raw_value)
        for index, value in parsed_values:
            entries.append((directive, index, key, value))

    entries.sort(key=lambda entry: (entry[0].lower(), entry[1], entry[2]))
    return [f"{directive} {value}" for directive, _, _, value in entries]


def _format_exit_nodes(value):
    if value == "":
        return ""

    exit_nodes = [node.strip().strip("'") for node in value.split(",") if node.strip()]
    if not exit_nodes:
        return ""

    return "{" + "},{".join(exit_nodes) + "}"


def _load_bridges(bridges_value, bridges_file_path=None):
    bridges_file = Path(bridges_file_path or "bridges.lst")
    if bridges_file.exists():
        with open(bridges_file, "rt") as file_bridges:
            return "1", file_bridges.read()

    bridges = [bridge.strip().strip("'") for bridge in bridges_value.split(",") if bridge.strip()]
    if not bridges:
        return "0", ""

    return "1", "\n".join(bridges) + "\n"


def mask_torrc_line(line):
    directive, _, value = line.partition(" ")
    if any(keyword in directive.lower() for keyword in SENSITIVE_TORRC_KEYWORDS):
        return f"{directive} [MASKED]"
    return f"{directive} {value}".rstrip()


def render_torrc_config(
    env=None,
    *,
    new_circuit_period=120,
    max_circuit_dirtiness=600,
    circuit_build_timeout=60,
    template_path="templates/tor.cfg",
    bridges_file_path=None,
):
    if env is None:
        env = os.environ

    with open(template_path, "rt") as file:
        template = jinja2.Template(file.read())

    exit_nodes = _format_exit_nodes(env.get("TOR_EXIT_NODES", ""))
    use_bridges, bridges = _load_bridges(env.get("TOR_BRIDGES", ""), bridges_file_path=bridges_file_path)
    extra_torrc_lines = build_torrc_passthrough_lines(env)

    config = template.render(
        new_circuit_period=new_circuit_period,
        max_circuit_dirtiness=max_circuit_dirtiness,
        circuit_build_timeout=circuit_build_timeout,
        exit_nodes=exit_nodes,
        use_bridges=use_bridges,
        bridges=bridges,
        extra_torrc_lines=extra_torrc_lines,
    )

    return config, extra_torrc_lines
