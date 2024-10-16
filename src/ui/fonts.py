import os

from kivy.core.text import LabelBase

from src.contstants import DEFAULT_FONT_NAME

LabelBase.register(
    name=DEFAULT_FONT_NAME,
    fn_regular=os.path.join(
        os.path.dirname(
            os.path.abspath(__file__)
        ),
        'static/SourceCodePro-Regular.ttf'
    )
)
