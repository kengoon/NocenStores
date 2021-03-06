from kivy.uix.screenmanager import Screen
from kivy import platform

if platform == "android":
    import android_webview


class StudentInfo(Screen):
    def go_home(self):
        self.manager.current = "home"

    def open_web(self):
        if platform == "android":
            android_webview.webbrowser.open("https://google.com")

        print("opened")
