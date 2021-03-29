from kivy.uix.screenmanager import Screen
from json import loads, dumps
from os import environ
from kivy.utils import get_color_from_hex
from kivymd.uix.button import MDRaisedButton

from libs.libpy.cartcheckout import DropDown
from kivymd.app import MDApp
from kivy.network.urlrequest import UrlRequest
from kivymd_extensions.sweetalert import SweetAlert


class Payment(Screen):
    app = MDApp.get_running_app()
    url = "https://nocenstore.pythonanywhere.com/"

    def go_back(self):
        self.manager.current = "checkout"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.payload = {}
        self.alert = SweetAlert()
        self.menu_set = False
        with open("bank.json") as file:
            self.banks = loads(file.read())
        menu_items = [{"icon": "bank", "text": i} for i in self.banks]
        self.menu = DropDown(
            items=menu_items,
            width_mult=4
        )
        self.menu.bind(on_release=self.set_item)

    def on_enter(self, *args):
        if not self.menu_set:
            self.menu.caller = self.ids.bank_name
            self.menu_set = True

    def set_item(self, instance_menu, instance_menu_item):
        self.ids.bank_name.text = instance_menu_item.text
        instance_menu.dismiss()

    def make_payment_bank(self):
        YES = MDRaisedButton(
            text='PROCEED',
            font_size=16,
            on_release=lambda x: self.proceed_with_bank_payment(),
        )
        NO = MDRaisedButton(
            text='NO',
            font_size=16,
            on_release=lambda x: self.alert.dismiss()
        )
        NO.md_bg_color = get_color_from_hex('#dd3b34')
        self.alert = SweetAlert()
        self.alert.fire(
            "Your Bank Will Be Debited, Do You Want To Proceed?",
            type="question",
            buttons=[YES, NO]
        )

    def proceed_with_bank_payment(self):
        try:
            self.alert.content_cls.children[1].text = "Processing Your Request"
            self.alert.request = True
            self.alert.auto_dismiss = False
            self.payload = {
                "accountnumber": self.ids.acc_no.text,
                "accountbank": self.banks[self.ids.bank_name.text],
                "currency": "NGN",
                "country": "NG",
                "amount": self.app.total_payment,
                "email": self.app.current_email,
                "phonenumber": self.app.current_phone,
                "firstname": self.app.firebase["name"].split(" ")[1],
                "lastname": self.app.firebase["name"].split(" ")[0],
                "IP": "355426087298442",
            }
            UrlRequest(
                self.url + "bankPayment",
                req_body=dumps(self.payload),
                on_success=self.bank_payment_successful,
                on_error=self.payment_unsuccessful,
                on_failure=self.server_error
            )
        except KeyError:
            self.alert.dismiss()
            self.alert = SweetAlert()
            self.alert.fire("Please Select A Valid Bank Name and And Account Number", type="warning")

    def bank_payment_successful(self, instance, data):
        self.alert.dismiss()
        payload = loads(data)
        if payload["validationRequired"]:
            self.payload.update(payload)
            self.payload.update({"product": self.app.data_product, "location": self.app.current_location})
            SUBMIT = MDRaisedButton(
                text='SUBMIT',
                font_size=16,
                on_release=lambda x: self.submit_bank_otp(),
            )
            CANCEL = MDRaisedButton(
                text='CANCEL',
                font_size=16,
                on_release=lambda x: self.alert.dismiss()
            )
            CANCEL.md_bg_color = get_color_from_hex('#dd3b34')
            self.alert = SweetAlert()
            self.alert.fire(
                title="Enter the OTP that was sent to your phone! Didn't get the OTP? Dial * 322 * 0 # on "
                      "your phone (MTN, Etisalat, Airtel) Glo, use * 805 * 0 #",
                type="info",
                input="otp",
                buttons=[SUBMIT, CANCEL]
            )
            self.alert.content_cls.children[1].input_filter = "int"
            self.alert.auto_dismiss = False

    def submit_bank_otp(self):
        self.alert.content_cls.children[2].text = "Processing Your Request"
        self.alert.content_cls.children[1].disabled = True
        self.payload.update({"otp": self.alert.content_cls.children[1].text})
        self.alert.request = True

        def submit_otp(instance, data):
            self.alert.dismiss()
            self.alert = SweetAlert()
            self.alert.fire("Payment Successfully Completed", type="success")

        UrlRequest(
            self.url + "submitBankOtp",
            req_body=dumps(self.payload),
            on_success=submit_otp,
            on_failure=self.server_error,
            on_error=self.payment_unsuccessful
        )

    def make_payment_card(self):
        YES = MDRaisedButton(
            text='PROCEED',
            font_size=16,
            on_release=lambda x: self.proceed_with_card_payment(),
        )
        NO = MDRaisedButton(
            text='NO',
            font_size=16,
            on_release=lambda x: self.alert.dismiss()
        )
        NO.md_bg_color = get_color_from_hex('#dd3b34')
        self.alert = SweetAlert()
        self.alert.fire(
            "Your Card Will Be Debited, Do You Want To Proceed?",
            type="question",
            buttons=[YES, NO]
        )

    def bank_payment_unsuccessful(self, *args):
        self.alert.dismiss()
        self.alert = SweetAlert()
        self.alert.fire("Network Error!", type="failure")

    def bank_server_error(self, *args):
        self.alert.dismiss()
        self.alert = SweetAlert()
        self.alert.fire("Transaction Failed! Check Your Bank Details, You Can Use Card instead", type='failure')

    def proceed_with_card_payment(self):
        self.alert.content_cls.children[1].text = "Processing Your Request"
        self.alert.request = True
        self.alert.auto_dismiss = False
        self.payload = {
            "cardno": self.ids.card_number.text,
            "cvv": self.ids.cvv.text,
            "pin": self.ids.pin.text,
            "location": self.app.current_location,
            "expirymonth": self.ids.month.text,
            "expiryyear": self.ids.year.text,
            "amount": self.app.total_payment,
            "email": self.app.current_email,
            "phonenumber": self.app.current_phone,
            "firstname": self.app.firebase["name"].split(" ")[1],
            "lastname": self.app.firebase["name"].split(" ")[0],
            "IP": "355426087298442",
        }
        UrlRequest(
            self.url + "cardPayment",
            req_body=dumps(self.payload),
            on_success=self.payment_successful,
            on_error=self.payment_unsuccessful,
            on_failure=self.server_error
        )

    def payment_successful(self, instance, data):
        self.alert.dismiss()
        if data == "success":
            return
        payload = loads(data)
        if payload["validationRequired"]:
            self.payload.update(payload)
            self.payload.update({"product": self.app.data_product, "location": self.app.current_location})
            SUBMIT = MDRaisedButton(
                text='SUBMIT',
                font_size=16,
                on_release=lambda x: self.submit_otp(),
            )
            CANCEL = MDRaisedButton(
                text='CANCEL',
                font_size=16,
                on_release=lambda x: self.alert.dismiss()
            )
            CANCEL.md_bg_color = get_color_from_hex('#dd3b34')
            self.alert = SweetAlert()
            self.alert.fire(
                title="Enter the OTP that was sent to your phone! Didn't get the OTP? Dial * 322 * 0 # on "
                      "your phone (MTN, Etisalat, Airtel) Glo, use * 805 * 0 #",
                type="info",
                input="otp",
                buttons=[SUBMIT, CANCEL]
            )
            self.alert.content_cls.children[1].input_filter = "int"
            self.alert.auto_dismiss = False

    def submit_otp(self):
        self.alert.content_cls.children[2].text = "Processing Your Request"
        self.alert.content_cls.children[1].disabled = True
        self.payload.update({"otp": self.alert.content_cls.children[1].text})
        self.alert.request = True

        def submit_otp(instance, data):
            self.alert.dismiss()
            self.alert = SweetAlert()
            self.alert.fire("Payment Successfully Completed", type="success")

        UrlRequest(
            self.url + "submitOtp",
            req_body=dumps(self.payload),
            on_success=submit_otp,
            on_failure=self.server_error,
            on_error=self.payment_unsuccessful

        )

    def payment_unsuccessful(self, *args):
        self.alert.dismiss()
        self.alert = SweetAlert()
        self.alert.fire("Network Error!", type="failure")

    def server_error(self, *args):
        self.alert.dismiss()
        self.alert = SweetAlert()
        self.alert.fire("Transaction Failed! Check Your Card Details", type='failure')
