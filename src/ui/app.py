from kivy.app import App as KivyApp
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget

from src.contstants import (NET_CONNECTIONS_INTERVAL,
                            NET_STATS_CONNECTIONS_INTERVAL,
                            NET_TRAFFIC_INTERVAL)
from src.logic import NetObserver

from .traffic import TrafficGrid


class App(KivyApp):
    title_label_styles = {
        'font_size': '24sp',
        'color': (1, 0.5, 0, 1),
        'bold': True,
        'halign': 'center',
        'size_hint_y': None,
        'height': 50
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.net_obs = NetObserver(
            NET_CONNECTIONS_INTERVAL,
            NET_STATS_CONNECTIONS_INTERVAL,
            NET_TRAFFIC_INTERVAL
        )

        self.traffic_grid = TrafficGrid(self.net_obs)

    def build(self):
        layout = BoxLayout(orientation='vertical', padding=10)

        traffic_title = Label(text='Traffic Stats', **self.title_label_styles)
        traffic_title.bind(size=traffic_title.setter('text_size'))
        layout.add_widget(traffic_title)

        layout.add_widget(self.traffic_grid)

        with layout.canvas.before:
            Color(0.1, 0.1, 0.1, 1)
            self.rect = Rectangle(size=layout.size, pos=layout.pos)

        layout.bind(size=self._update_rect, pos=self._update_rect)

        return layout

    def _update_rect(self, instance: Widget, _: tuple) -> None:
        self.rect.pos = instance.pos
        self.rect.size = instance.size
