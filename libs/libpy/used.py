from kivy.uix.screenmanager import Screen
from kivymd.uix.menu import MDDropdownMenu


class Used(Screen):
    update = None
    menu = None

    def on_enter(self, *args):
        if not self.update:
            # self.menu = MDDropdownMenu(
            #     caller=self.ids.menu,
            #     items=[
            #         {"icon": "account", "text": "profile"},
            #         {"icon": "cog", "text": "settings"},
            #     ],
            #     width_mult=4,
            #     position="auto"
            # )
            pass
    pass
