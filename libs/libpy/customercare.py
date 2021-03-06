from kivy.uix.screenmanager import Screen
from kivymd.toast import toast
from plyer import call, email


class CustomerCare(Screen):
    def go_home(self):
        self.manager.current = "home"

    @staticmethod
    def send(instance):
        email.send(
            recipient="nocenstore@gmail.com", subject="Customer Support",
            text=instance.parent.text, create_chooser=False
        )
        toast("select gmail or email when app chooser opens", length_long=True)

    @staticmethod
    def call_customer_care():
        call.makecall("08129330697")
