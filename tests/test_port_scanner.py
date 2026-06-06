import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from scanners.port_scanner import scan_port, COMMON_PORTS, RISKY_PORTS


class TestScanPort:
    def test_closed_port_returns_none(self):
        """A port that is definitely closed should return None."""
        # Port 1 is almost never open
        result = scan_port("127.0.0.1", 1)
        assert result is None

    def test_open_port_returns_dict(self):
        """Localhost port 80 may not be open, but structure should be correct
        if it is."""
        result = scan_port("127.0.0.1", 80)
        if result is not None:
            assert "port" in result
            assert "service" in result
            assert "risky" in result

    def test_result_has_correct_port_number(self):
        """If a port is open, the returned port number should match."""
        result = scan_port("127.0.0.1", 80)
        if result is not None:
            assert result["port"] == 80

    def test_risky_flag_is_boolean(self):
        """The risky field should always be a boolean."""
        result = scan_port("127.0.0.1", 80)
        if result is not None:
            assert isinstance(result["risky"], bool)


class TestPortConstants:
    def test_common_ports_not_empty(self):
        """COMMON_PORTS should have entries."""
        assert len(COMMON_PORTS) > 0

    def test_risky_ports_subset_of_common(self):
        """All risky ports should exist in COMMON_PORTS."""
        for port in RISKY_PORTS:
            assert port in COMMON_PORTS

    def test_known_ports_present(self):
        """Key well-known ports should be in COMMON_PORTS."""
        assert 80 in COMMON_PORTS
        assert 443 in COMMON_PORTS
        assert 22 in COMMON_PORTS
        assert 53 in COMMON_PORTS

    def test_risky_ports_flagged_correctly(self):
        """SMB and Telnet should be in risky ports."""
        assert 445 in RISKY_PORTS
        assert 23 in RISKY_PORTS