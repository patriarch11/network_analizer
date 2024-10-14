import ipaddress as ip
import re
from dataclasses import dataclass

import psutil as ps
from psutil._common import sconn, snicaddr


@dataclass
class AddressConnections:
    address: 'NetworkInterfaceAddress'
    connections: list[sconn]


class NetworkInterfaceAddress:
    @staticmethod
    def is_mac_addr(addr: str) -> bool:
        return bool(re.match(
            r'^([0-9A-Fa-f]{2}[:\-]){5}([0-9A-Fa-f]{2})$',
            addr
        ))

    def __init__(self, info: snicaddr) -> None:
        self._info = info

    @property
    def address(self) -> str:
        return self._info.address

    @property
    def ip_adress(self) -> ip.IPv4Address | ip.IPv6Address:
        return ip.ip_address(self.address)

    @property
    def is_mac(self) -> bool:
        return self.is_mac_addr(self.address)

    def is_addr_match(self, addr: str) -> bool:
        is_match = False
        if self.is_mac_addr(addr):
            if self.is_mac:
                is_match = addr == self.address
            else:
                is_match = False
        elif not self.is_mac:
            is_match = ip.ip_address(addr) == self.ip_adress
        return is_match


class NetworkInterface:
    def __init__(self, name: str) -> None:
        self.name = name
        self._addresses: list[NetworkInterfaceAddress] = []

        self._assign_addresses()

    def _assign_addresses(self):
        interfaces = ps.net_if_addrs()

        if not interfaces.get(self.name):
            raise Exception(f'Network interface {self.name} does\'n exists')

        for address in interfaces[self.name]:
            self._addresses.append(NetworkInterfaceAddress(address))

    def _ps_conn_filter(self, conn: sconn) -> bool:
        for addr in self._addresses:
            if addr.is_addr_match(conn.laddr.ip):  # type: ignore
                return True
        return False

    def get_connections(self) -> list[AddressConnections]:
        connections = list(
            filter(
                lambda conn: self._ps_conn_filter(conn),
                ps.net_connections()
            )
        )
        return [
            AddressConnections(
                address=addr,
                connections=list(
                    filter(
                        lambda conn: addr.is_addr_match(
                            conn.laddr.ip),  # type: ignore
                        connections
                    )
                )
            )
            for addr in self._addresses
        ]


def get_network_interfaces() -> list[NetworkInterface]:
    return [NetworkInterface(name) for name in ps.net_if_addrs()]
