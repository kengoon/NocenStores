from json import loads, dumps
from typing import Union, NoReturn

from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
from kivy.factory import Factory
from kivy.network.urlrequest import UrlRequest
from kivy.properties import StringProperty, ObjectProperty, BooleanProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.modalview import ModalView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.relativelayout import RelativeLayout
from kivymd.toast import toast
from kivymd.uix.behaviors import FakeRectangularElevationBehavior, MagicBehavior
from kivymd.uix.button.button import BaseRoundButton, MDFloatingActionButton
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.dropdownitem import MDDropDownItem
from kivymd.uix.list import OneLineIconListItem
from kivy import platform
from kivy.animation import Animation
from kivy.app import App
from kivy.properties import NumericProperty, ListProperty
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex
from kivymd.theming import ThemableBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.core.window import Window
from kivymd.uix.textfield import MDTextField
from kivymd_extensions.akivymd.uix.bottomnavigation2 import AKBottomNavigation2
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.menu.menu import m_res
from kivy.metrics import dp
from kivymd_extensions.akivymd.uix.dialogs import AKAlertDialog

from classes.notification import notify
from libs.classes_wigdet.m_cardtextfield import M_CardTextField
from tools import check_add_widget

app = App.get_running_app()
m_res.STANDARD_INCREMENT = dp(150)
URL = "https://nocenstore.pythonanywhere.com/"


class MD3Card(MDCard, FakeRectangularElevationBehavior):
    pass


class DropDown(MDDropdownMenu):
    def set_menu_properties(self, interval: Union[int, float] = 0) -> NoReturn:
        """Sets the size and position for the menu window."""

        if not self.caller:
            return
        self.ids.md_menu.data = self.items
        # We need to pick a starting point, see how big we need to be,
        # and where to grow to.
        self._start_coords = self.caller.to_window(
            self.caller.center_x / 2.8, self.caller.center_y
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
        # each MDMenuItem or MDMenuItemIcon.
        self.target_height = 0
        for item in self.ids.md_menu.data:
            self.target_height += item.get("height", dp(72))

        # If we're over max_height...
        if 0 < self.max_height < self.target_height:
            self.target_height = self.max_height

            # Establish vertical growth direction.
        if self.ver_growth is not None:
            ver_growth = self.ver_growth
        elif (
                        self.target_height
                        <= self._start_coords[1] - self.border_margin
                ):
            ver_growth = "down"
        elif (
                self.target_height
                < Window.height - self._start_coords[1] - self.border_margin
        ):
            ver_growth = "up"
        elif (
                            self._start_coords[1]
                            >= Window.height - self._start_coords[1]
                    ):
            ver_growth = "down"
            self.target_height = (
                    self._start_coords[1] - self.border_margin
            )
        else:
            ver_growth = "up"
            self.target_height = (
                    Window.height
                    - self._start_coords[1]
                    - self.border_margin
            )

        if self.hor_growth is not None:
            hor_growth = self.hor_growth
        elif (
                        self.target_width
                        <= Window.width - self._start_coords[0] - self.border_margin
                ):
            hor_growth = "right"
        elif (
                self.target_width
                < self._start_coords[0] - self.border_margin
        ):
            hor_growth = "left"
        elif (
                            Window.width - self._start_coords[0]
                            >= self._start_coords[0]
                    ):
            hor_growth = "right"
            self.target_width = (
                    Window.width
                    - self._start_coords[0]
                    - self.border_margin
            )
        else:
            hor_growth = "left"
            self.target_width = (
                    self._start_coords[0] - self.border_margin
            )
        if ver_growth == "down":
            self.tar_y = self._start_coords[1] - self.target_height
        else:  # should always be "up"
            self.tar_y = self._start_coords[1]

        if hor_growth == "right":
            self.tar_x = self._start_coords[0]
        else:  # should always be "left"
            self.tar_x = self._start_coords[0] - self.target_width
        self._calculate_complete = True


class Locator(MDDropDownItem):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with open("location.json") as file:
            self.locations = loads(file.read())
            self.locations.pop("UNIZIK Temp Site Junction Awka")
        menu_items = [
            {
                "viewclass": "DropListItem",
                "icon": "map-marker-radius",
                "text": f"{i}",
                "height": dp(56),
                "on_release": lambda x=f"{i}": self.set_item(x),
            }
            for i in self.locations
        ]
        self.menu = DropDown(
            items=menu_items,
            width_mult=2,
            caller=self,
            hor_growth="right",
        )

    def set_item(self, value):
        self.text = value
        self.menu.dismiss()


class ItemPagination(ThemableBehavior, Widget):
    current_index = NumericProperty(0)
    color_round_not_active = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.color_round_not_active:
            self.color_round_not_active = get_color_from_hex("#757575")


class Swiper(MDBoxLayout):
    @staticmethod
    def swipe_pagnitors(instance, index):
        for pagnitor in instance.pagnitors:
            if instance.pagnitors[index] == pagnitor:
                Animation(rgba=app.theme_cls.primary_color, d=0.3).start(pagnitor.canvas.children[0])
                continue
            Animation(rgba=pagnitor.color_round_not_active, d=0.3).start(pagnitor.canvas.children[0])


class DropListItem(OneLineIconListItem):
    icon = StringProperty()


class CategoryCard(ButtonBehavior, MDBoxLayout):
    texture_color = ListProperty(get_color_from_hex("#FFFFFF"))


class HomeProductCard(RecycleDataViewBehavior, MDBoxLayout):
    update = False
    texture = ObjectProperty(None)
    imagePath = ObjectProperty()
    canvas_texture = None
    source = ObjectProperty()
    rv = None
    index = 0


class TopLayerHome(MDBoxLayout):
    root = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.category_dialog = MDDialog(
            title="Categories",
            type="custom",
            content_cls=Factory.CategoryContent(),
            radius=[dp(30)]
        )
        self.category_dialog.content_cls.dialog = self.category_dialog
        self.platform_dialog = MDDialog(
            title="Sections",
            type="custom",
            content_cls=Factory.PlatformContent(),
            radius=[dp(30)]
        )
        self.platform_dialog.content_cls.dialog = self.platform_dialog


class CircularIcon(BaseRoundButton):
    icon = StringProperty("checkbox-blank-circle")


class BottomNavigation(FakeRectangularElevationBehavior, AKBottomNavigation2):
    elevation = NumericProperty(10)
    radius = NumericProperty("40dp")


class BaseProductCard(RecycleDataViewBehavior, MD3Card):
    pass


# class BaseSalesCard(RecycleDataViewBehavior, MD3Card):
#     index = 0
#
#     def refresh_view_attrs(self, rv, index, data):
#         self.index = index
#         super(BaseSalesCard, self).refresh_view_attrs(rv, index, data)
#
#     def store_image_state(self):
#         print(self.parent)


class PhoneCardTextField(M_CardTextField):
    def on_text(self, *args):
        if not args:
            return
        if len(args[1]) > 11:
            self.text = self.text[:-1]


class PlanItem(ThemableBehavior, MagicBehavior, MDBoxLayout):
    text_item = StringProperty()
    border = StringProperty()
    color_select = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color_select = self.theme_cls.disabled_hint_text_color
        self.primary = self.theme_cls.primary_color

    def press_on_plan(self, instance_plan):
        self.parent.root.root.selected_size = self.text_item
        for widget in self.parent.children:
            if widget.color_select == self.primary:
                widget.color_select = self.color_select
                self.grow()
                break
        instance_plan.color_select = self.primary


class PhoneTextField(MDTextField):
    def insert_text(self, substring, from_undo=False):
        new_text = self.text + substring
        if new_text != '' and len(new_text) < 12:
            MDTextField.insert_text(self, substring, from_undo=from_undo)

    def on_text(self, instance, text):
        instance.error = len(text) != 11

    @staticmethod
    def do_focus(value):
        if platform == "android":
            from kvdroid import activity
            from android.runnable import run_on_ui_thread

            @run_on_ui_thread
            def fix_back_button():
                activity.onWindowFocusChanged(False)
                activity.onWindowFocusChanged(True)

            if not value:
                fix_back_button()


class RequestDialog(MDBoxLayout):
    text = StringProperty("")
    dialog = ObjectProperty()
    btn_disabled = BooleanProperty(False)
    icon = StringProperty("gift-open")


class FloatingButton(MDFloatingActionButton, MagicBehavior):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.spinner_view = ModalView(size_hint=(.5, .5), background="", background_color=[0, 0, 0, 0])
        dialog_box = RequestDialog(
            text="checking if you qualify for free airtime today......",
            dialog=self.spinner_view,
        )
        self.spinner_view.add_widget(dialog_box)
        self.spinner_view.bind(on_dismiss=self.cancel_request)
        self.spinner_view.bind(on_open=self.request_free_airtime)
        self.spinner_view.auto_dismiss = False
        self.request = None
        self.dialog = AKAlertDialog(
            header_icon="check-circle-outline", header_bg=[0, 0.7, 0, 1],
            size_hint=(.75, .5)
        )
        content = Factory.SuccessDialog()
        self.dialog.content_cls = content
        self.dialog.content_cls.root = self
        self.dialog.content_cls.dialog = self.dialog
        self.alert_dialog = AKAlertDialog(
            header_icon="bell",
            progress_interval=5,
            fixed_orientation="landscape",
            pos_hint={"right": 1, "y": 0.05},
            dialog_radius=10,
            size_landscape=["350dp", "70dp"],
            header_width_landscape="70dp",
        )
        self.alert_dialog.bind(on_progress_finish=self.alert_dialog.dismiss)
        content = Factory.AlertNotification()
        content.ids.button.bind(on_release=self.alert_dialog.dismiss)
        self.alert_dialog.content_cls = content

    def on_kv_post(self, base_widget):
        Clock.schedule_interval(lambda x: self.twist(), 3)

    def request_free_airtime(self, instance):
        if not app.login:
            self.add_login_screen()
            self.spinner_view.dismiss()
            return
        self.request = UrlRequest(
            url=f"{URL}airtime",
            on_failure=self.server_error,
            on_success=self.request_completed,
            on_error=self.network_error
        )

    def server_error(self, *_):
        notify("SERVER ERROR.....")
        self.spinner_view.dismiss()

    def network_error(self, *_):
        notify("IT SEEMS YOU LOST INTERNET CONNECTION...")
        self.spinner_view.dismiss()

    def request_completed(self, *args):
        self.spinner_view.dismiss()
        if args[1]:
            self.dialog.content_cls.ids.label.text = args[1]
            self.dialog.open()
        else:
            self.alert_dialog.open()

    def cancel_request(self, instance):
        if self.request:
            self.request.cancel()

    def add_login_screen(self):
        notify("please login to continue")
        app.current = "home"
        self.root.manager.prev_screen.append(self.root.name)
        from tools import check_add_widget
        check_add_widget(app, "login_widget", self.root, "Factory.Login()", "login")
        self.root.manager.current = "login"


class CustomSpinner(MDFloatingActionButton, MagicBehavior):
    pass


class SuccessDialog(BoxLayout):
    def copy_to_clipboard(self, text: str):
        if "airtel" in text:
            dial = f"*126*{text.split(':')[1].strip(' ')}#"
        elif "mtn" in text:
            dial = f"*555*{text.split(':')[1].strip(' ')}#"
        elif "glo" in text:
            dial = f"*123*{text.split(':')[1].strip(' ')}#"
        else:
            dial = f"*222*{text.split(':')[1].strip(' ')}#"
        self.dialog.dismiss()
        Clipboard.copy(dial)
        toast("Copied To Clipboard: Paste it on the dialer")
        from kvdroid.jimplement.call import dial_call
        dial_call(dial)

    def dial_airtime(self, text: str):
        if "airtel" in text:
            dial = f"*126*{text.split(':')[1].strip(' ')}#"
        elif "mtn" in text:
            dial = f"*555*{text.split(':')[1].strip(' ')}#"
        elif "glo" in text:
            dial = f"*123*{text.split(':')[1].strip(' ')}#"
        else:
            dial = f"*222*{text.split(':')[1].strip(' ')}#"
        self.dialog.dismiss()
        Clipboard.copy(dial)
        toast("Copied To Clipboard")
        from kvdroid.jimplement.call import make_call
        make_call(dial)


class PlatformContent(RelativeLayout):
    def change_screen(self, var, factory, screen_name, item):
        home_screen = app.root.ids.manager.children[0].ids.home
        screen_manager = app.root.ids.manager.children[0]
        screen_manager.on_next_screen(home_screen.name)
        check_add_widget(app, var, home_screen, factory, screen_name)
        screen_manager.current = item
        self.dialog.dismiss()
