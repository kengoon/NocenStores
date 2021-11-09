from json import loads

from kivy.core.window import Window
from kivy.factory import Factory
from kivy.metrics import dp
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.relativelayout import RelativeLayout
from kivymd.uix.behaviors import FakeRectangularElevationBehavior, MagicBehavior
from kivymd.uix.button.button import BaseRoundButton
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineIconListItem
from kivy import platform
from kivy.animation import Animation
from kivy.app import App
from kivy.properties import NumericProperty, ListProperty
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex
from kivymd.theming import ThemableBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd_extensions.akivymd.uix.bottomnavigation2 import AKBottomNavigation2

from libs.classes_wigdet.m_cardtextfield import M_CardTextField
from libs.libpy.cartcheckout import DropDown

app = App.get_running_app()


class Locator(MDTextField):
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
            width_mult=4,
            caller=self
        )
        self.menu.bind(on_release=self.set_item)

    def set_item(self, value):
        self.text = value
        self.menu.dismiss()

    def on_focus(self, *args):
        if args[1]:
            self.menu.open()
        if platform == "android":
            from kvdroid import activity
            from android.runnable import run_on_ui_thread

            @run_on_ui_thread
            def fix_back_button():
                activity.onWindowFocusChanged(False)
                activity.onWindowFocusChanged(True)

            if not args[1]:
                fix_back_button()

    def insert_text(self, substring, from_undo=False):
        pass


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
        self.platform_dialog = MDDialog(
            title="Sections",
            type="custom",
            content_cls=Factory.PlatformContent(),
            radius=[dp(30)]
        )

    def call_category_dialog(self):
        self.category_dialog.content_cls.dialog = self.category_dialog
        self.category_dialog.content_cls.root = self.root
        self.category_dialog.open()

    def call_platform_dialog(self):
        self.platform_dialog.content_cls.dialog = self.platform_dialog
        self.platform_dialog.content_cls.root = self.root
        self.platform_dialog.open()


class CircularIcon(BaseRoundButton):
    icon = StringProperty("checkbox-blank-circle")


class BottomNavigation(FakeRectangularElevationBehavior, AKBottomNavigation2):
    elevation = NumericProperty(10)
    radius = NumericProperty("40dp")


class BaseProductCard(RecycleDataViewBehavior, MDCard):
    pass


# class BaseSalesCard(RecycleDataViewBehavior, MDCard):
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
