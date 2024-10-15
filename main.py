from logic.network import NetObserver

if __name__ == '__main__':
    obs = NetObserver(1, 1, 1)
    m = obs.connections_monitor()
    for _ in range(5):
        print(next(m))
    m = obs.stats_monitor()
    for _ in range(5):
        print(next(m))
    m = obs.traffic_monitor()
    for _ in range(5):
        print(next(m))
