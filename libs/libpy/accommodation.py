from kivy import platform
from kivy.uix.recycleview import RecycleView
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView


class Accommodation(Screen):
    pass


class Scroller(ScrollView):
    def on_scroll_move(self, touch):
        pass
        # if touch.button in ["scrollup", "scrolldown"]:
        #     print("dkjdj")
        #     self.root.root.dispatch("on_scroll_move", touch)


