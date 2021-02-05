from kivy.factory import Factory
from kivy.uix.screenmanager import Screen
from kivymd.uix.dialog import MDDialog


class Review(Screen):
    def go_home(self):
        self.manager.current = "home"

    def comment_dialog(self):
        MDDialog(
            title="Leave A Comment",
            type="custom",
            content_cls=Factory.CommentField()
        )