from json import dumps, loads

from kivy.core.window import Window, Animation
from kivy.factory import Factory
from kivy.metrics import dp
from kivy.uix.image import AsyncImage
from kivy.uix.modalview import ModalView
from kivy.utils import get_color_from_hex
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd_extensions.sweetalert import SweetAlert

from classes.notification import notify
from kivy.network.urlrequest import UrlRequest
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from plyer import call

from libs.libpy.widgets import DropDown


class ProductLookOut(Screen):
    url = "https://nocenstore.pythonanywhere.com/"
    tmp_data = None
    _tmp_data = None
    selected_size = ""
    app = MDApp.get_running_app()
    p_type = ""
    toast = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.alert = None
        self.dialog = MDDialog(
            title="Size",
            type="custom",
            content_cls=Factory.SizeSelector(),
            radius=[dp(20)]
        )
        self.dialog.content_cls.root = self
        self.image_view_content = AsyncImage()
        self.image_view = ModalView(size_hint=(.5, .5), background="", background_color=[0, 0, 0, 0])
        self.image_view.add_widget(self.image_view_content)
        menu_items = [
            {
                "viewclass": "ThreeLineIconList",
                "icon": f"{i[0]}",
                "text": f"{i[1]}",
                "secondary_text": f"{i[2]}",
                "tertiary_text": f"{i[3]}",
                "height": dp(80),
            }
            for i in [
                [
                    "truck-delivery-outline",
                    "Product Delivery",
                    "Ready for delivery between 2 to 3 days ",
                    "from the day you ordered",
                ],
                [
                    "police-badge-outline",
                    "Return Policy",
                    "Free return within a day and",
                    "Full Refund if you do not get your package delivered"
                ]
            ]
        ]
        self.menu = DropDown(
            items=menu_items,
            width_mult=2.1,
            # caller=self.ids.info,
            hor_growth="right",
        )

    def go_back(self):
        self.manager.current = "home"

    def fire(self, request_number, text=""):
        logout = MDRaisedButton(text="CANCEL", on_release=lambda x: self.alert.dismiss())
        logout.md_bg_color = get_color_from_hex('#dd3b34')
        self.alert = SweetAlert(size_hint_x=None, width=Window.width - dp(20))
        self.alert.fire(
            text or "Do you want to proceed with call to order",
            buttons=[MDRaisedButton(text="CONTINUE", on_release=lambda x: request_number()),
                     logout],
            type="question"
        )

    def call_customer_care(self, *args):

        def get_number(instance, data):
            self.alert.dismiss()
            call.makecall(data)

        def network_error():
            self.alert.dismiss()
            self.alert = SweetAlert(size_hint_x=None, width=Window.width - dp(20))
            self.alert.fire("Network Error", type="failure")

        def request_number():
            self.alert.content_cls.children[1].text = "Requesting For Any Online Customer Care Line"
            self.alert.request = True
            UrlRequest(
                self.url + "getNumber",
                on_success=get_number,
                req_body=args[1] if args else "order",
                on_error=lambda x, y: network_error(),
            )

        self.fire(request_number, args[0] if args else "")

    def on_enter(self, *args):
        self.manager.ids.home.dispatch("on_enter")

    def enter_cart(self):
        self.app.current = self.name
        self.manager.prev_screen.append(self.name)
        from tools import check_add_widget
        check_add_widget(self.app, "cart_widget", self, "Factory.Cart()", "cart")
        self.manager.current = "cart"

    def on_leave(self, *args):
        self.clear_cache()

    def update_interface(self, data):
        self.tmp_data = data
        new_data = data.copy()
        if self.app.login:
            new_data.update({"userId": self.app.firebase["userId"]})
        UrlRequest(
            url=f"{self.url}showcaseProduct",
            req_body=dumps(new_data),
            on_error=self.network_error,
            on_success=self.post_data
        )

    def network_error(self, *args):
        if self.toast:
            notify("You lost connection, check your Internet settings")
            self.toast = False
        self.update_interface(self.tmp_data)

    def post_data(self, instance, data):
        new_data = loads(data)
        self._tmp_data = new_data.copy()
        self.ids.product_price.text = \
            f"[font=Roboto]₦[/font]{float(new_data['price']) + 5 / 100 * float(new_data['price']):,}"
        self.ids.description.text = new_data["description"].split("size(")[0]
        for i in range(1, 4):
            self.ids[f"image{i}"].source = new_data[str(i)]

        if "size" in new_data["description"]:
            size_list = new_data["description"].split("(")[1].split(")")[0]
            size_list = size_list.replace("{", "[").replace("}", "]")
            for i in loads(size_list):
                self.dialog.content_cls.data.append({"text_item": str(i)})
        self.ids.buttons.disabled = False
        self.ids.buttons.opacity = 1
        if "saved" in new_data and new_data["saved"]:
            self.ids.save.icon = "heart"
        if new_data["type"] == "FairlyUsed":
            self.ids.save.disabled = True
            self.p_type = new_data["type"]
        else:
            self.ids.save.disabled = False
            self.p_type = ""

    def swipe_pagnitors(self, instance, index):
        for pagnitor in instance.pagnitors:
            if instance.pagnitors[index] == pagnitor:
                Animation(rgba=self.app.theme_cls.primary_color, d=0.3).start(pagnitor.canvas.children[0])
                continue
            Animation(rgba=pagnitor.color_round_not_active, d=0.3).start(pagnitor.canvas.children[0])

    def clear_cache(self):
        for i in range(1, 4):
            self.ids[f"image{i}"].source = "assets/image/loader.gif"
        self.ids.product_price.text = "____"
        self.ids.description.text = ""
        self.dialog.content_cls.data = []

    def save_unsave(self, instance):
        if not self.app.login:
            notify("please login to continue")
            self.app.current = self.name
            from tools import check_add_widget
            check_add_widget(self.app, "login_widget", self, "Factory.Login()", "login")
            self.manager.current = "login"
            return
        instance.icon = "heart" if "outline" in instance.icon else "heart-outline"
        instance.disabled = True

        def process(instance_object, data):
            notify(data)
            instance.disabled = False
            from tools import check_add_widget
            check_add_widget(self.app, "saved_product_widget", self, "Factory.SavedProduct()", "saved")
            if self.manager.ids.saved.enter:
                self.manager.ids.saved.ids.rv.data.append(
                    {
                        "imagePath": self.ids.image1.source,
                        "price":
                            self.ids.product_price.text.translate({ord(i): None for i in "[font=Roboto][/font]₦,"}),
                        "product": self.ids.product_name.text,
                        "store": "NocenStore"
                    }
                )

        def network_error(*args):
            notify("network error, please subscribe")
            instance.disabled = False
            instance.icon = "heart" if "outline" in instance.icon else "heart-outline"

        def server_error(*args):
            notify("server is down, fixing...")
            instance.disabled = False
            instance.icon = "heart" if "outline" in instance.icon else "heart-outline"

        data = {
            self.ids.product_name.text: {
                "imagePath": self.ids.image1.source,
                "price": self.ids.product_price.text.replace("₦", ""),
                "product": self.ids.product_name.text,
                "store": "NocenStore",
            },
            "type": instance.icon,
            "userId": self.app.firebase["userId"],
            "idToken": self.app.firebase["idToken"]
        }
        UrlRequest(
            url=self.url + "saveMyProduct",
            req_body=dumps(data),
            on_success=process,
            on_error=network_error,
            on_failure=server_error
        )

    def add_to_cart(self):
        from tools import check_add_widget
        check_add_widget(self.app, "cart_widget", self, "Factory.Cart()", "cart")
        if self.dialog.content_cls.data and not self.selected_size:
            notify("select a  size to continue", background=[1, 0, 0, 1])
            return self.dialog.open()
        if not self.app.login:
            notify("please login to continue")
            self.app.current = self.name
            self.manager.prev_screen.append(self.name)
            check_add_widget(self.app, "login_widget", self, "Factory.Login()", "login")
            self.manager.current = "login"
            return
        cart = {
            "product": self.ids.product_name.text,
            "source": self.ids.image1.source,
            "price": self.ids.product_price.text,
            "store": "NocenStore",
            "selected_size": self.selected_size or "",
            "count": 1,
            "base_price": self.ids.product_price.text.translate(
                {ord(i): None for i in "[font=Roboto][/font]₦,"}
            ),
        }

        product_exist = list(filter(lambda product: self.ids.product_name.text == product["product"],
                                    self.manager.ids.cart.ids.rv.data))
        if product_exist:
            if self.p_type == "FairlyUsed":
                from tools import check_add_widget
                check_add_widget(self.app, "cart_widget", self, "Factory.Cart()", "cart")
                self.manager.current = "cart"
                return
            cart["p_type"] = False
            cart["count"] = product_exist[0]["count"]
            total = float(product_exist[0]["price"].translate({ord(i): None for i in "[font=Roboto][/font]₦,"})) + \
                    float(cart["price"].translate({ord(i): None for i in "[font=Roboto][/font]₦,"}))
            top_up = f'[font=Roboto]₦{total:,}[/font]'
            cart["price"] = product_exist[0]["price"]
            index = self.manager.ids.cart.ids.rv.data.index(cart)
            cart["count"] += 1
            cart["price"] = top_up
            self.manager.ids.cart.ids.rv.data[index] = cart
            notify(f"{self.ids.product_name.text} = {self.manager.ids.cart.ids.rv.data[index]['count']} product")
        else:
            cart["p_type"] = self.p_type == "FairlyUsed"
            self.manager.ids.cart.ids.rv.data.append(cart)
            notify(f"{self.ids.product_name.text} = 1 product")
            if self.p_type == "FairlyUsed":
                from tools import check_add_widget
                check_add_widget(self.app, "cart_widget", self, "Factory.Cart()", "cart")
                self.manager.current = "cart"
                cart_data = self.manager.ids.cart.ids.rv.data
                cart_total = sum(
                    float(cart_data[i]["price"].translate({ord(i): None for i in "[font=Roboto][/font]₦,"})) for
                    i, _ in enumerate(cart_data)
                )
                self.manager.ids.cart.ids.total.text = f"[font=Roboto]₦{cart_total:,}[/font]"
                return
        check_add_widget(self.app, "cart_widget", self, "Factory.Cart()", "cart")
        self.manager.current = "cart"
        self.ids.save.dispatch("on_release") if self.ids.save.icon == "heart-outline" else None
        cart_data = self.manager.ids.cart.ids.rv.data
        cart_total = sum(
            float(cart_data[i]["price"].translate({ord(i): None for i in "[font=Roboto][/font]₦,"})) for
            i, _ in enumerate(cart_data)
        )
        self.manager.ids.cart.ids.total.text = f"[font=Roboto]₦{cart_total:,}[/font]"

    def show_image(self, source):
        self.image_view_content.source = source
        self.image_view.open()
