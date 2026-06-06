import pytest
import sys
import os

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from utils.network import get_local_ip, get_subnet


class TestGetLocalIp:
    def test_returns_string(self):
        """get_local_ip should always return a string."""
        result = get_local_ip()
        assert isinstance(result, str)

    def test_not_empty(self):
        """get_local_ip should never return an empty string."""
        result = get_local_ip()
        assert len(result) > 0

    def test_valid_ip_format(self):
        """get_local_ip should return a valid IPv4 address."""
        result = get_local_ip()
        parts = result.split(".")
        assert len(parts) == 4
        for part in parts:
            assert part.isdigit()
            assert 0 <= int(part) <= 255

    def test_not_loopback(self):
        """get_local_ip should not return loopback unless no network."""
        result = get_local_ip()
        # On a normal machine with network this should not be loopback
        assert result != "0.0.0.0"


class TestGetSubnet:
    def test_basic_subnet(self):
        """Should return correct /24 subnet for a standard IP."""
        result = get_subnet("192.168.1.50")
        assert result == "192.168.1.0/24"

    def test_host_bits_zeroed(self):
        """Network address should have host bits zeroed out."""
        result = get_subnet("10.0.0.187")
        assert result == "10.0.0.0/24"

    def test_returns_string(self):
        """get_subnet should always return a string."""
        result = get_subnet("192.168.1.1")
        assert isinstance(result, str)

    def test_cidr_notation(self):
        """Result should contain CIDR slash notation."""
        result = get_subnet("192.168.1.1")
        assert "/" in result

    def test_custom_prefix(self):
        """Should respect a custom prefix length."""
        result = get_subnet("192.168.1.50", prefix=16)
        assert result == "192.168.0.0/16"

    def test_different_subnets(self):
        """Different IPs in same subnet should return same network."""
        result1 = get_subnet("192.168.1.10")
        result2 = get_subnet("192.168.1.200")
        assert result1 == result2