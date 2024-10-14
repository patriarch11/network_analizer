from logic.net_interface import get_network_interfaces

if __name__ == '__main__':
    for ifc in get_network_interfaces():
        print(ifc.name)

        for c in ifc.get_connections():
            print('\t', c.address.address)
            for cc in c.connections:
                print('\t\t', cc.status, cc.pid, cc.laddr.port, '->', cc.raddr)
        print('---')
