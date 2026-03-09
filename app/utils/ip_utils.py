"""IP address utilities"""
import ipaddress
from typing import Optional

def is_valid_ip(ip: str) -> bool:
    """Check if string is a valid IP address"""
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def is_private_ip(ip: str) -> bool:
    """Check if IP is in private range"""
    try:
        return ipaddress.ip_address(ip).is_private
    except ValueError:
        return False

def get_ip_info(ip: str) -> dict:
    """Get information about an IP address"""
    try:
        addr = ipaddress.ip_address(ip)
        return {
            "ip": str(addr),
            "version": addr.version,
            "is_private": addr.is_private,
            "is_loopback": addr.is_loopback,
            "is_multicast": addr.is_multicast,
            "is_global": addr.is_global,
        }
    except ValueError:
        return {"error": "Invalid IP address"}

def ip_in_range(ip: str, cidr: str) -> bool:
    """Check if IP is in CIDR range"""
    try:
        return ipaddress.ip_address(ip) in ipaddress.ip_network(cidr)
    except ValueError:
        return False

def get_network_info(cidr: str) -> Optional[dict]:
    """Get network information from CIDR"""
    try:
        network = ipaddress.ip_network(cidr)
        return {
            "network": str(network.network_address),
            "broadcast": str(network.broadcast_address),
            "netmask": str(network.netmask),
            "num_addresses": network.num_addresses,
            "prefixlen": network.prefixlen,
        }
    except ValueError:
        return None
