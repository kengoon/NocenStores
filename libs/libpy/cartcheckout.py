import re
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.menu.menu import m_res
from kivy.metrics import dp
from json import loads
from kivy.core.window import Window
from classes.notification import notify

m_res.STANDARD_INCREMENT = dp(150)


class DropDown(MDDropdownMenu):
    def set_menu_properties(self, interval=0):  # sourcery no-metrics
        """Sets the size and position for the menu window."""

        if not self.caller:
            return
        if not self.menu.ids.box.children:
            self.create_menu_items()
        # We need to pick a starting point, see how big we need to be,
        # and where to grow to.
        self._start_coords = self.caller.to_window(
            self.caller.x, self.caller.center_y
        )
        self.target_width = self.width_mult * m_res.STANDARD_INCREMENT

        # If we're wider than the Window...
        if self.target_width > Window.width:
            # ...reduce our multiplier to max allowed.
            self.target_width = (
                    int(Window.width / m_res.STANDARD_INCREMENT)
                    * m_res.STANDARD_INCREMENT
            )

        # Set the target_height of the menu depending on the size of
        # each MDMenuItem or MDMenuItemIcon
        self.target_height = 0
        for item in self.menu.ids.box.children:
            self.target_height += item.height

        # If we're over max_height...
        if 0 < self.max_height < self.target_height:
            self.target_height = self.max_height

            # Establish vertical growth direction.
        if self.ver_growth is None:
            # If there's enough space below us:
            if (
                    self.target_height
                    <= self._start_coords[1] - self.border_margin
            ):
                ver_growth = "down"
            # if there's enough space above us:
            elif (
                    self.target_height
                    < Window.height - self._start_coords[1] - self.border_margin
            ):
                ver_growth = "up"
            # Otherwise, let's pick the one with more space and adjust ourselves.
            else:
                # If there"s more space below us:
                if (
                        self._start_coords[1]
                        >= Window.height - self._start_coords[1]
                ):
                    ver_growth = "down"
                    self.target_height = (
                            self._start_coords[1] - self.border_margin
                    )
                # If there's more space above us:
                else:
                    ver_growth = "up"
                    self.target_height = (
                            Window.height
                            - self._start_coords[1]
                            - self.border_margin
                    )

        else:
            ver_growth = self.ver_growth
        if self.hor_growth is None:
            # If there's enough space to the right:
            if (
                    self.target_width
                    <= Window.width - self._start_coords[0] - self.border_margin
            ):
                hor_growth = "right"
            # if there's enough space to the left:
            elif (
                    self.target_width
                    < self._start_coords[0] - self.border_margin
            ):
                hor_growth = "left"
            # Otherwise, let's pick the one with more space and adjust ourselves.
            else:
                # if there"s more space to the right:
                if (
                        Window.width - self._start_coords[0]
                        >= self._start_coords[0]
                ):
                    hor_growth = "right"
                    self.target_width = (
                            Window.width
                            - self._start_coords[0]
                            - self.border_margin
                    )
                # if there"s more space to the left:
                else:
                    hor_growth = "left"
                    self.target_width = (
                            self._start_coords[0] - self.border_margin
                    )

        else:
            hor_growth = self.hor_growth
        if ver_growth == "down":
            self.tar_y = self._start_coords[1] - self.target_height
        else:  # should always be "up"
            self.tar_y = self._start_coords[1]

        if hor_growth == "right":
            self.tar_x = self._start_coords[0]
        else:  # should always be "left"
            self.tar_x = self._start_coords[0] - self.target_width
        self._calculate_complete = True


class CartCheckOut(Screen):
    app = MDApp.get_running_app()
    regex = [
        '^[a-z0-9]+[\\._]?[a-z0-9]+[@]\\w+[.]\\w+[.]\\w{2,3}$',
        '^[a-z0-9]+[\\._]?[a-z0-9]+[@]\\w+[.]\\w{2,3}$'
    ]

    def go_back(self):
        self.ids.location.text = ""
        self.manager.current = "cart"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.menu_set = False
        with open("location.json") as file:
            self.locations = loads(file.read())
        menu_items = [{"icon": "map-marker-radius", "text": i} for i in self.locations]
        self.menu = DropDown(
            items=menu_items,
            width_mult=4
        )
        self.menu.bind(on_release=self.set_item)

    def on_enter(self, *args):
        self.ids.email.text = self.app.firebase["email"]
        self.ids.phone.text = self.app.firebase["phone"]
        if not self.menu_set:
            self.menu.caller = self.ids.location
            self.menu_set = True

    def set_item(self, instance_menu, instance_menu_item):
        self.ids.location.text = instance_menu_item.text
        self.ids.fee.right_text = self.locations[instance_menu_item.text]
        total = float(self.manager.ids.cart.ids.total.text.translate({ord(i): None for i in '₦,'})) + \
                float(self.locations[instance_menu_item.text].translate({ord(i): None for i in '₦,'}))
        self.ids.total.right_text = f"₦{total:,}"
        self.app.total_payment = total
        instance_menu.dismiss()

    def proceed(self):
        if len(self.ids.phone.text) != 11:
            return notify("incorrect phone number")
        if not re.search(self.regex[1], self.ids.email.text) and not re.search(self.regex[0], self.ids.email.text):
            return notify("incorrect email format", background=[0.2, 0.2, 0.2, 1])
        self.manager.prev_screen.append(self.name)
        self.manager.current = "payment"
        self.app.current_email = self.ids.email.text
        self.app.current_phone = self.ids.phone.text
        self.app.current_location = self.ids.location.text
