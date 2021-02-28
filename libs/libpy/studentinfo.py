from kivy.uix.screenmanager import Screen


class StudentInfo(Screen):
    def go_home(self):
        self.manager.current = "home"
