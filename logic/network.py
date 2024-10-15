import ipaddress as ip
import re
import time
from dataclasses import dataclass
from typing import Generator

import psutil as ps
from psutil._common import NicDuplex, sconn, snicaddr, snicstats


@dataclass
class NetConnections:
    address: 'NetAddress'
    connections: list[sconn]


@dataclass
class NetIfConnections:
    interface: 'NetIf'
    connections: list[NetConnections]


@dataclass
class NetIfStats:
    interface: 'NetIf'
    is_active: bool
    duplex: NicDuplex
    speed: int
    mtu: int
    flags: str


@dataclass
class TrafficInfo:
    sent_bytes: int
    recv_bytes: int
    packets_sent: int
    packets_recv: int
    err_in: int
    err_out: int
    drop_in: int
    drop_out: int
    interval_s: int


class NetAddress:
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


class NetIf:
    def __init__(self, name: str) -> None:
        self.name = name
        self._addresses: list[NetAddress] = []

        self._assign_addresses()

    def _assign_addresses(self):
        interfaces = ps.net_if_addrs()

        if not interfaces.get(self.name):
            raise Exception(f'Network interface {self.name} does\'n exists')

        for address in interfaces[self.name]:
            self._addresses.append(NetAddress(address))

    def _ps_conn_filter(self, conn: sconn) -> bool:
        for addr in self._addresses:
            if addr.is_addr_match(conn.laddr.ip):  # type: ignore
                return True
        return False

    def extract_connections(self, conns: list[sconn]) -> list[NetConnections]:
        connections = list(
            filter(
                lambda conn: self._ps_conn_filter(conn),
                conns
            )
        )
        return [
            NetConnections(
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

    def extract_stats(self, stast: dict[str, snicstats]) -> NetIfStats:
        stats = stast.get(self.name)
        if not stats:
            raise Exception(f'Missing stats for net interface {self.name}')

        return NetIfStats(
            interface=self,
            is_active=stats.isup,
            duplex=NicDuplex(stats.duplex),
            speed=stats.speed,
            mtu=stats.mtu,
            flags=stats.flags
        )


class NetObserver:
    def __init__(
        self,
        connections_interval_s: int,
        stats_interval_s: int,
        traffic_interval_s: int
    ) -> None:
        self._connections_interval_s = connections_interval_s
        self._stats_interval_s = stats_interval_s
        self._traffic_interval_s = traffic_interval_s
        self._net_interfaces = [
            NetIf(name) for name in ps.net_if_addrs()
        ]

    def connections_monitor(self) -> Generator[
            list[NetIfConnections], None, None
    ]:
        while True:
            connections = ps.net_connections()

            time.sleep(self._connections_interval_s)
            yield [
                NetIfConnections(
                    ifc, ifc.extract_connections(connections)
                )
                for ifc in self._net_interfaces
            ]

    def stats_monitor(self) -> Generator[list[NetIfStats], None, None]:
        while True:
            stats = ps.net_if_stats()

            time.sleep(self._connections_interval_s)
            yield [ifc.extract_stats(stats) for ifc in self._net_interfaces]

    def traffic_monitor(self) -> Generator[TrafficInfo, None, None]:
        old = ps.net_io_counters()

        while True:
            time.sleep(self._traffic_interval_s)
            new = ps.net_io_counters()

            info = TrafficInfo(
                sent_bytes=new.bytes_sent - old.bytes_sent,
                recv_bytes=new.bytes_recv - old.bytes_recv,
                packets_sent=new.packets_sent - old.packets_sent,
                packets_recv=new.packets_recv - old.packets_recv,
                err_in=new.errin - old.errin,
                err_out=new.errout - old.errout,
                drop_in=new.dropin - old.dropin,
                drop_out=new.dropout - old.dropout,
                interval_s=self._traffic_interval_s
            )

            old = new

            yield info
