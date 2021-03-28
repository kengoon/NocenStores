from json import dumps, loads
from kivy.uix.screenmanager import Screen
import re
from kivy.network.urlrequest import UrlRequest
from classes.notification import notify
from kivymd.app import MDApp

app = MDApp.get_running_app()
url = "https://nocenstore.pythonanywhere.com/"


class Login(Screen):
    def login_account(self):
        for i in self.ids:
            try:
                if self.ids[i].text == "":
                    self.disabled = False
                    self.ids.spinner.active = False
                    notify("please fill all fields", background=[0.2, 0.2, 0.2, 1], duration=7)
                    return
            except AttributeError:
                pass
        self.disabled = True
        data = dumps({"email": self.ids.email.text, "password": self.ids.password.text})
        UrlRequest(
            url=url + "login",
            req_body=data,
            on_error=self.network_error,
            on_failure=self.server_error,
            on_success=self.collect_save_data
        )

    @staticmethod
    def see_unset_password(instance):
        instance.parent.password = instance.parent.password != True
        instance.icon = "eye-off" if instance.icon == "eye" else "eye"

    def network_error(self, *args):
        self.disabled = False
        self.ids.spinner.active = False
        notify("please check your network connection", background=[0.2, 0.2, 0.2, 1])

    def server_error(self, *args):
        self.disabled = False
        self.ids.spinner.active = False
        notify("Incorrect Email or Password or it seems You haven't created an account yet,"
               " please click on create an account!!!",
               [0.2, 0.2, 0.2, 1], duration=10)

    def collect_save_data(self, instance, data):
        self.disabled = False
        self.ids.spinner.active = False
        user_data = loads(data)
        with open("token.json", "w") as file:
            file.write(dumps(user_data, indent=4, sort_keys=True))
        app.login = True
        app.firebase = user_data
        self.manager.current = app.current or "home"
        if app.current:
            self.manager.ids.lookout.ids.buttons.disabled = True
            self.manager.ids.lookout.clear_cache()
            self.manager.ids.lookout.update_interface(self.manager.ids.lookout.tmp_data)
        app.current = ""
        self.manager.ids.home.ids.profiles.ids.user.text = f"Welcome {app.firebase['name']}!"
        self.manager.ids.home.ids.profiles.ids.email.text = app.firebase["email"]
        print(self.manager.ids.setting.ids.rule1.ids)


class SignUp(Screen):
    regex = [
        '^[a-z0-9]+[\\._]?[a-z0-9]+[@]\\w+[.]\\w+[.]\\w{2,3}$',
        '^[a-z0-9]+[\\._]?[a-z0-9]+[@]\\w+[.]\\w{2,3}$'
    ]

    @staticmethod
    def see_unset_password(instance):
        instance.parent.password = instance.parent.password != True
        instance.icon = "eye-off" if instance.icon == "eye" else "eye"

    def create_account(self):
        for instance in self.ids:
            try:
                if self.ids[instance].text == "":
                    self.opacity = 1
                    self.ids.spinner.active = False
                    notify("please fill all fields", background=[0.2, 0.2, 0.2, 1], duration=7)
                    return
            except AttributeError:
                pass
        if len(self.ids.phone.text) < 11:
            self.opacity = 1
            self.ids.spinner.active = False
            notify("please make sure you type in your 11 digit phone number", background=[0.2, 0.2, 0.2, 1])
            return
        if not re.search(self.regex[1], self.ids.email.text) and not re.search(self.regex[0], self.ids.email.text):
            self.opacity = 1
            self.ids.spinner.active = False
            notify("incorrect email format", background=[0.2, 0.2, 0.2, 1])
            return
        if len(self.ids.password.text) < 8:
            self.opacity = 1
            self.ids.spinner.active = False
            notify("password must be up to 8 characters", background=[0.2, 0.2, 0.2, 1])
            return
        if self.ids.password.text != self.ids.confirm_password.text:
            self.opacity = 1
            self.ids.spinner.active = False
            notify("confirm password does not match password", background=[0.2, 0.2, 0.2, 1])
            return

        self.disabled = True
        data = dumps({
            "name": self.ids.name.text,
            "email": self.ids.email.text,
            "phone": self.ids.phone.text,
            "password": self.ids.password.text
        })
        UrlRequest(
            url=url + "signup",
            req_body=data,
            on_error=self.network_error,
            on_failure=self.server_error,
            on_success=self.collect_save_data
        )

    def network_error(self, *args):
        self.disabled = False
        self.opacity = 1
        self.ids.spinner.active = False
        print(args[1])
        notify("please check your network connection", background=[0.2, 0.2, 0.2, 1])

    def server_error(self, *args):
        self.disabled = False
        self.opacity = 1
        self.ids.spinner.active = False
        print(args[1])
        notify("it looks like your email address already exist on our server, please sign in!!!",
               [0.2, 0.2, 0.2, 1], duration=10)

    def collect_save_data(self, instance, data):
        self.disabled = False
        self.ids.spinner.active = False
        user_data = loads(data)
        user_data.update({"name": self.ids.name.text, "email": self.ids.email.text, "phone": self.ids.phone.text})
        with open("token.json", "w") as file:
            file.write(dumps(user_data, indent=4, sort_keys=True))
        app.login = True
        app.firebase = user_data
        self.manager.current = app.current or "home"
        if app.current:
            self.manager.ids.lookout.ids.buttons.disabled = True
            self.manager.ids.lookout.clear_cache()
            self.manager.ids.lookout.update_interface(self.manager.ids.lookout.tmp_data)
        app.current = ""
        print(app.firebase)
        self.manager.ids.home.ids.profiles.ids.user.text = f"Welcome {app.firebase['name']}!"
        self.manager.ids.home.ids.profiles.ids.email.text = app.firebase["email"]
