"""
Unit tests for the GUI entry point.

The desktop GUI is not implemented; gui_main must fail fast with a clear
message rather than launch a misleading placeholder window.
"""
import pytest

from nmap_ai.gui.main import gui_main


def test_gui_main_exits_nonzero_with_message(capsys):
    with pytest.raises(SystemExit) as exc:
        gui_main()
    assert exc.value.code != 0

    err = capsys.readouterr().err
    assert "not available yet" in err
    assert "nmap-ai" in err  # points users to the CLI
