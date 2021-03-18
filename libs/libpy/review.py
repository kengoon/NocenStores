from kivy.core.window import Window
from kivy.factory import Factory
from kivy.metrics import dp
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivymd.uix.dialog import MDDialog


class Review(Screen):
    dialog = ObjectProperty()

    def go_home(self):
        self.manager.current = "home"

    def enter_search(self):
        self.manager.prev_screen.append(self.name)
        self.manager.current = "search"

    def comment_dialog(self):
        self.dialog = MDDialog(
            title="Leave A Comment",
            type="custom",
            content_cls=CommentField(root=self),
            size_hint_x=None,
            width=Window.width - dp(20)
        )
        self.dialog.open()

    def send_comment(self, instance):
        self.dialog.dismiss()


class CommentField(BoxLayout):
    root = ObjectProperty()
