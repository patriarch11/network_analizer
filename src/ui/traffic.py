from threading import Thread

from kivy.clock import Clock
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label

from src.contstants import DEFAULT_FONT_NAME
from src.logic import NetObserver, NetTraffic


class TrafficGrid(GridLayout):
    styles = {
        'cols': 1,
        'rows': 4,
        'padding': [10, 5, 10, 5],
        'spacing': 2
    }

    label_styles = {
        'font_name': DEFAULT_FONT_NAME,
        'halign': 'left',
        'size_hint_y': None,
        'height': 30,
        'text_size': (500, None),
        'markup': True
    }

    class templates:
        k_bytes = 'Traffic kB/s: [color=00FF00]↓[/color] {recv:<8}    {sent:>8} [color=FF0000]↑[/color]'  # noqa
        packets = 'Packets/s:    [color=00FF00]↓[/color] {recv:<8}    {sent:>8} [color=FF0000]↑[/color]'  # noqa
        errors = 'Errors/s:     [color=00FF00]↓[/color] {in_:<8}    {out:>8} [color=FF0000]↑[/color]'  # noqa
        drops = 'Drops/s:      [color=00FF00]↓[/color] {in_:<8}    {out:>8} [color=FF0000]↑[/color]'  # noqa

    def __init__(self, net_obs: NetObserver):
        super().__init__(**self.styles)
        self.net_obs = net_obs

        self.bytes_label = Label(**self.label_styles)
        self.packets_label = Label(**self.label_styles)
        self.err_label = Label(**self.label_styles)
        self.drop_label = Label(**self.label_styles)

        self.add_widget(self.bytes_label)
        self.add_widget(self.packets_label)
        self.add_widget(self.err_label)
        self.add_widget(self.drop_label)

        Thread(target=self.run_monitor, daemon=True).start()

    def run_monitor(self):
        for info in self.net_obs.traffic_monitor():
            Clock.schedule_once(lambda _: self.update(info))

    def update(self, info: NetTraffic):
        self.bytes_label.text = self.templates.k_bytes.format(
            recv=f'{info.recv_bytes / 1024:.2f}',
            sent=f'{info.sent_bytes / 1024:.2f}'
        )
        self.packets_label.text = self.templates.packets.format(
            recv=info.packets_recv,
            sent=info.packets_sent
        )

        self.err_label.text = self.templates.errors.format(
            in_=info.err_in,
            out=info.err_out
        )

        self.drop_label.text = self.templates.drops.format(
            in_=info.drop_in,
            out=info.drop_out
        )
