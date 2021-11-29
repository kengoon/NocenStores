import re

from kivy.metrics import dp
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from json import loads
from classes.notification import notify
from libs.libpy.widgets import DropDown


class CartCheckOut(Screen):
    app = MDApp.get_running_app()
    regex = [
        '^[a-z0-9]+[\\._]?[a-z0-9]+[@]\\w+[.]\\w+[.]\\w{2,3}$',
        '^[a-z0-9]+[\\._]?[a-z0-9]+[@]\\w+[.]\\w{2,3}$'
    ]

    def go_back(self):
        self.ids.location.text = ""
        from tools import check_add_widget
        check_add_widget(self.app, "cart_widget", self, "Factory.Cart()", "cart")
        self.manager.current = "cart"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.menu_set = False
        self.menu = None
        with open("location.json") as file:
            self.locations = loads(file.read())
        menu_items = [
            {
                "viewclass": "DropListItem",
                "icon": "map-marker-radius",
                "text": i, "height": dp(56),
                "on_release": lambda x=f"{i}": self.set_item(self.menu, x)
            }
            for i in self.locations]
        self.menu = DropDown(
            items=menu_items,
            width_mult=2,
            hor_growth="right"
        )

    def on_enter(self, *args):
        self.ids.email.text = self.app.firebase["email"]
        self.ids.phone.text = self.app.firebase["phone"]
        if not self.menu_set:
            self.menu.caller = self.ids.location
            self.menu_set = True

    def set_item(self, instance_menu, instance_menu_item):
        self.ids.location.text = instance_menu_item
        self.ids.fee.right_text = f"[font=Roboto]{self.locations[instance_menu_item]}[/font]"
        total = (
            float(self.manager.ids.cart.ids.total.text.translate({ord(i): None for i in '[font=Roboto][/font]₦,'})) +
            float(self.locations[instance_menu_item].translate({ord(i): None for i in '[font=Roboto][/font]₦,'}))
        )
        self.ids.total.right_text = f"[font=Roboto]₦{total:,}[/font]"
        self.app.total_payment = total
        instance_menu.dismiss()

    def proceed(self):
        if len(self.ids.phone.text) != 11:
            return notify("incorrect phone number")
        if not re.search(self.regex[1], self.ids.email.text) and not re.search(self.regex[0], self.ids.email.text):
            return notify("incorrect email format", background=[0.2, 0.2, 0.2, 1])
        self.manager.prev_screen.append(self.name)
        from tools import check_add_widget
        check_add_widget(self.app, "payment_widget", self, "Factory.Payment()", "payment")
        self.manager.current = "payment"
        self.app.current_email = self.ids.email.text
        self.app.current_phone = self.ids.phone.text
        self.app.current_location = self.ids.location.text
