from kivy.clock import Clock
from kivy.properties import ObjectProperty, NumericProperty
from kivy.uix.screenmanager import ScreenManager


class Manager(ScreenManager):
    prev_screen = []

    # do_layout_event = ObjectProperty(None, allownone=True)
    #
    # layout_delay_s = NumericProperty(0.2)
    #
    # def do_layout(self, *args, **kwargs):
    #     if self.do_layout_event is not None:
    #         self.do_layout_event.cancel()
    #     real_do_layout = super().do_layout
    #     self.do_layout_event = Clock.schedule_once(
    #         lambda dt: real_do_layout(*args, **kwargs),
    #         self.layout_delay_s)
    
    def on_next_screen(self, prev_screen):
        self.prev_screen.append(prev_screen)

    def on_back_button(self):
        self.current = self.prev_screen.pop()
