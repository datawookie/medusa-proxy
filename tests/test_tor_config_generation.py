import tempfile

from proxy.torrc import render_torrc_config


def test_safe_logging_line_is_appended():
    config, extra_lines = render_torrc_config(env={"TORRC_SafeLogging": "1"})

    assert "SafeLogging 1" in config
    assert extra_lines == ["SafeLogging 1"]


def test_json_list_expands_to_repeated_directives():
    config, extra_lines = render_torrc_config(
        env={"TORRC_EXIT_POLICY": '["reject *:*", "accept *:443"]'}
    )

    assert extra_lines == ["ExitPolicy reject *:*", "ExitPolicy accept *:443"]
    assert "ExitPolicy reject *:*" in config
    assert "ExitPolicy accept *:443" in config


def test_passthrough_precedence_over_managed_directive():
    config, _ = render_torrc_config(
        env={"TORRC_New_Circuit_Period": "240"},
        new_circuit_period=120,
    )

    managed_position = config.find("NewCircuitPeriod            120")
    override_position = config.rfind("NewCircuitPeriod 240")

    assert managed_position != -1
    assert override_position != -1
    assert override_position > managed_position


def test_exit_nodes_generation_is_preserved():
    config, _ = render_torrc_config(env={"TOR_EXIT_NODES": "ru,en"})
    assert "ExitNodes {ru},{en}" in config


def test_bridge_env_generation_is_preserved():
    config, _ = render_torrc_config(env={"TOR_BRIDGES": "Bridge one,Bridge two"})

    assert "UseBridges 1" in config
    assert "Bridge one" in config
    assert "Bridge two" in config


def test_bridge_file_takes_priority_over_environment():
    with tempfile.NamedTemporaryFile(mode="wt", delete=True) as bridge_file:
        bridge_file.write("Bridge from file\n")
        bridge_file.flush()

        config, _ = render_torrc_config(
            env={"TOR_BRIDGES": "Bridge from env"},
            bridges_file_path=bridge_file.name,
        )

    assert "UseBridges 1" in config
    assert "Bridge from file" in config
    assert "Bridge from env" not in config
