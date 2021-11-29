from json import dumps

from kivy.metrics import dp
from kivymd.uix.list import IconLeftWidget

from classes.notification import notify
from kivy.factory import Factory
from kivy.network.urlrequest import UrlRequest
from kivy.uix.screenmanager import Screen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelOneLine
from kivymd.app import MDApp


class Setting(Screen):
    app = MDApp.get_running_app()
    url = "https://nocenstore.pythonanywhere.com/"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = MDDialog(
            type="custom",
            content_cls=Factory.Loader()
        )
        self.dialog.auto_dismiss = False

    def go_home(self):
        self.manager.current = "home"

    def add_all_rules(self, rule1, rule2):
        def loop_add_rule(rules, ids):
            for index, rule in enumerate(rules.items):
                expansion_panel = MDExpansionPanel(
                    content=rules.content[index],
                    panel_cls=MDExpansionPanelOneLine(text=rule)
                )
                expansion_panel.panel_cls._txt_left_pad = dp(20)
                rules.add_widget(expansion_panel)
                rules.ids[f"_{ids}{index}"] = rules.content[index]

        loop_add_rule(rule1, "r1")
        loop_add_rule(rule2, "r2")
        if self.app.firebase:
            rule1.ids._r10.ids.name.text = f'Name: {self.app.firebase["name"]}'
            rule1.ids._r10.ids.email.text = f'Email: {self.app.firebase["email"]}'
            rule1.ids._r10.ids.phone.text = f'Phone: {self.app.firebase["phone"]}'

    def reset_password(self):
        self.dialog.open()

        def alert_error(*args):
            self.dialog.dismiss()
            notify("network error", background=[1, 0, 0, 1])

        def alert_success(*args):
            self.dialog.dismiss()
            notify("password reset link sent to your email\nvisit your email to change your password", duration=10)

        UrlRequest(
            url=self.url + "password_reset",
            req_body=dumps({"email": self.app.firebase["email"]}),
            on_success=alert_success,
            on_error=alert_error,
        )

    def change_number(self, number):
        if len(number) < 11:
            notify("please enter a valid number!!", background=[1, 0, 0, 1])
            return
        self.dialog.open()

        def alert_error(*args):
            self.dialog.dismiss()
            notify("network error", background=[1, 0, 0, 1])

        def alert_success(*args):
            self.dialog.dismiss()
            notify("phone number change success!!", duration=10)
            self.app.firebase["phone"] = number
            self.ids.rule1.ids._r10.ids.phone.text = f'Phone: {self.app.firebase["phone"]}'

        UrlRequest(
            url=self.url + "changePhoneNumber",
            req_body=dumps({"userId": self.app.firebase["userId"], "phone": number}),
            on_success=alert_success,
            on_error=alert_error,
        )

    def check_theme_active(self):
        with open("theme.txt", "w") as theme:
            theme.write("Dark") if self.app.theme_cls.theme_style == "Light" else theme.write("Light")
            self.app.theme_cls.theme_style = "Dark" if self.app.theme_cls.theme_style == "Light" else "Light"
