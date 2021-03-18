from kivy.uix.screenmanager import Screen


class Order(Screen):
    def go_home(self):
        self.manager.current = "home"

    def enter_search(self):
        self.manager.prev_screen.append(self.name)
        self.manager.current = "search"
