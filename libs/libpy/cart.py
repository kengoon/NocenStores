from json import dumps

from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp


class Cart(Screen):
    app = MDApp.get_running_app()

    def go_home(self):
        self.manager.current = self.app.current or "home"
        if self.app.current:
            self.manager.ids.lookout.clear_cache()
            self.manager.ids.lookout.post_data(None, dumps(self.manager.ids.lookout._tmp_data))
        self.app.current = ""
