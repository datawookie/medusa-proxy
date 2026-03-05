import pytest

from proxy.torrc import build_torrc_passthrough_lines


def test_single_directive():
    lines = build_torrc_passthrough_lines({"TORRC_SafeLogging": "1"})
    assert lines == ["SafeLogging 1"]


def test_repeated_directives_use_json_list():
    lines = build_torrc_passthrough_lines(
        {
            "TORRC_EXIT_POLICY": '["reject *:*", "accept *:443"]',
            "TORRC_SafeLogging": "1",
        }
    )
    assert lines == [
        "ExitPolicy reject *:*",
        "ExitPolicy accept *:443",
        "SafeLogging 1",
    ]


def test_indexed_variable_name_is_rejected():
    with pytest.raises(ValueError, match="Expected TORRC_<Directive>"):
        build_torrc_passthrough_lines({"TORRC_EXIT_POLICY__1": "reject *:*"})


def test_invalid_variable_name_raises():
    with pytest.raises(ValueError, match="Invalid environment variable"):
        build_torrc_passthrough_lines({"TORRC_9Bad": "1"})


def test_empty_value_raises():
    with pytest.raises(ValueError, match="empty value"):
        build_torrc_passthrough_lines({"TORRC_SafeLogging": "   "})


def test_duplicate_after_normalization_raises():
    with pytest.raises(ValueError, match="one variable per directive"):
        build_torrc_passthrough_lines(
            {
                "TORRC_SafeLogging": "1",
                "TORRC_SAFE_LOGGING": "0",
            }
        )


def test_multiline_value_raises():
    with pytest.raises(ValueError, match="JSON list"):
        build_torrc_passthrough_lines({"TORRC_SafeLogging": "1\n2"})


def test_invalid_json_list_raises():
    with pytest.raises(ValueError, match="valid JSON"):
        build_torrc_passthrough_lines({"TORRC_EXIT_POLICY": "[not-json]"})


def test_json_list_items_must_be_strings():
    with pytest.raises(ValueError, match="must be a string"):
        build_torrc_passthrough_lines({"TORRC_EXIT_POLICY": '["ok", 123]'})
