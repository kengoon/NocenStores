from kivy.uix.screenmanager import Screen
from kivymd.toast import toast
from plyer import call


class CustomerCare(Screen):
    def go_home(self):
        self.manager.current = "home"

    @staticmethod
    def send(instance):
        toast("message sent")

    @staticmethod
    def call_customer_care():
        call.makecall("08129330697")
