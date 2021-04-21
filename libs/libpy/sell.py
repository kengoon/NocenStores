import imghdr
import os
import re
from json import dumps
from os.path import exists, basename
from shutil import rmtree
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.network.urlrequest import UrlRequest
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from plyer import filechooser
from kivy import platform
from kivy.properties import ListProperty
from kivy.uix.screenmanager import Screen
from requests_toolbelt import MultipartEncoder

from classes.notification import notify
from PIL import Image


class Sell(Screen):
    images = []
    image_name = []
    data = ListProperty([])
    app = MDApp.get_running_app()
    image_sizes = []
    server_image = []
    binary_images = []
    image_type = []
    mime_type = []
    url = "https://nocenstore.pythonanywhere.com/"
    regex = [
        '^[a-z0-9]+[\\._]?[a-z0-9]+[@]\\w+[.]\\w+[.]\\w{2,3}$',
        '^[a-z0-9]+[\\._]?[a-z0-9]+[@]\\w+[.]\\w{2,3}$'
    ]
    ided = False
    update = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.widgets = [{"viewclass": "Title"}, {"viewclass": "PicArt", "root": self},
                        {"viewclass": "Fields", "root": self}]
        self.dialog = MDDialog(
            title="Uploading Your Product To Server",
            text="please wait while we upload your product. You can continue to check out our product,"
                 "we will give you a notice when we are done",
            size_hint_x=None,
            width=Window.width - dp(20)
        )
        self.dialog.auto_dismiss = True

    def on_enter(self, *args):
        if not self.update:
            for data in self.widgets:
                self.ids.rv.data.append(data)
            self.update = True

    @staticmethod
    def open_filechooser(instance):
        def call(file_list):
            if not file_list[0]:
                notify("do not select image from gallery, use normal file manager")
                return
            for i in [".png", ".jpg", ".jpeg", ".gif"]:
                if i in file_list[0].lower():
                    instance.source = file_list[0]
                    return
            if not instance.source:
                notify("please select an image file")
                return None

        if platform == "android":
            filechooser.open_file(preview=True, filters=["image"], on_selection=call, multiple=True)
        else:
            filechooser.open_file(preview=True, filters=["*.jpg", "*.png", "*.jpeg", "*.gif"],
                                  on_selection=call, multiple=True)

    def upload_product_data(self, name, des, price, phone, email, location, _pic1, _pic2, _pic3):
        if not self.ided:
            self.ids.update(
                {
                    "name": name,
                    "des": des,
                    "price": price,
                    "phone": phone,
                    "location": location,
                    "email": email,
                    "_pic1": _pic1,
                    "_pic2": _pic2,
                    "_pic3": _pic3
                }
            )
            self.ided = True
        if len(self.ids.phone.text) != 11:
            return notify("incorrect phone number")
        if not re.search(self.regex[1], self.ids.email.text) and not re.search(self.regex[0], self.ids.email.text):
            return notify("incorrect email format", background=[0.2, 0.2, 0.2, 1])
        self.make_room_for_new_items()
        instance = [name, des, price, phone, email, location, _pic1, _pic2, _pic3]
        self.images = [_pic1.text, _pic2.text, _pic3.text]
        for data in instance:
            if not data.text:
                notify("please fill all fields")
                return
        self.dialog.open()
        self.compress()
        self.collect_imb_imt()
        self.upload2server()

    # collect image binary and image type
    def collect_imb_imt(self):
        # loops through the list of the absolute path of compressed images and reads the binary image into a list
        for i, image in enumerate(self.server_image):
            with open(image, 'rb') as f:
                self.binary_images.append(f.read())

                # get the image type (png, jpg, jpeg...) and appends it to self.image_type for MultipartEncoder
                # handling
                self.image_type.append(imghdr.what(None, h=(self.binary_images[i])))
                self.mime_type.append(f"image/{self.image_type[i]}")

    def compress(self):
        if not exists('assets/compressed'):
            os.mkdir('assets/compressed')
        for _, im in enumerate(self.images):  # im is the image name
            image = Image.open(im)
            base_width = image.size[0]
            width_percentage = base_width / float(image.size[0])
            image_size = int(float(image.size[1] * float(width_percentage)))
            image = image.resize((base_width, image_size), Image.ANTIALIAS)
            self.image_sizes.append(image.size)  # appends the image resolution for MultipartEncoder handling
            image.save(f"assets/compressed/{str(_) + basename(im)}", optimize=True, quality=27)

            # appending the absolute path to the compressed image for uploading to the server
            self.server_image.append(f"assets/compressed/{str(_) + basename(im)}")

    def upload2server(self):
        im_name = [basename(image_name) for image_name in self.server_image]
        data = MultipartEncoder(fields=
                                {'product': self.ids.name.text, 'price': self.ids.price.text,
                                 'category': '', 'type': "FairlyUsed", "location": self.ids.location.text,
                                 'description': self.ids.des.text, 'store': self.ids.email.text.split("@")[0],
                                 'phone': self.ids.phone.text, 'im_size': dumps(self.image_sizes),
                                 'path1': f"{self.ids.email.text.split('@')[0]}/{self.ids.name.text}/{im_name[0]}",
                                 'path2': f"{self.ids.email.text.split('@')[0]}/{self.ids.name.text}/{im_name[1]}",
                                 'path3': f"{self.ids.email.text.split('@')[0]}/{self.ids.name.text}/{im_name[2]}",
                                 'file': (
                                     im_name[0], self.binary_images[0], self.mime_type[0]), 'file1': (
                                    im_name[1], self.binary_images[1], self.mime_type[1]), 'file2': (
                                    im_name[2], self.binary_images[2], self.mime_type[2])})
        UrlRequest(self.url + 'request4market_space',
                   req_body=data,
                   req_headers={'Content-Type': data.content_type},
                   on_success=self.market_opened,
                   on_failure=self.market_failed,
                   on_error=self.network_error)

    def make_room_for_new_items(self):
        self.images.clear()
        self.image_type.clear()
        self.mime_type.clear()
        self.binary_images.clear()
        self.server_image.clear()
        self.image_sizes.clear()

    def market_opened(self, *args):
        self.dialog.dismiss()
        notify("completed done")
        if exists("assets/compressed"):
            rmtree("assets/compressed")

        for instance in self.ids:
            # get all the variables that exist on the instance class
            try:
                members = [attr for attr in dir(self.ids[instance]) if
                           not callable(getattr(self.ids[instance], attr)) and not attr.startswith("__")]

                if "text" in members:
                    self.ids[instance].text = ""
                elif "source" in members:
                    self.ids[instance].source = ""
            except (KeyError, AttributeError):
                pass

    def market_failed(self, *args):
        self.dialog.dismiss()
        if exists("assets/compressed"):
            rmtree("assets/compressed")
        notify("server down", duration=10)

    def network_error(self, *args):
        self.dialog.dismiss()
        if exists("assets/compressed"):
            rmtree("assets/compressed")
        notify("We could not upload your product\nplease turn on your network or subscribe", duration=10)

    # def open_gallery(self):
    #     if self.root.manager.ids.picture.ids.rv.data:
    #         print("leaving")
    #         return
    #
    #     def _get_all_images():
    #         for dirs, _, files in os.walk("/home/kengo/Pictures" if platform != "android" else "/storage/emulated/0"):
    #             image_file = glob.glob(f"{dirs}/*.png") + glob.glob(f"{dirs}/*.jpeg") + glob.glob(f"{dirs}/*.jpg")
    #             for i in image_file:
    #                 if ("Android/" in i) or (i.startswith(".")):
    #                     continue
    #                 self.image_name.append(i.split("/")[-1])
    #                 self.images.append(os.path.join(dirs, i))
    #         for image, image_name in zip(self.images, self.image_name):
    #             self.data.append({"source": image, "text": image_name})
    #         Clock.schedule_once(self.push_data2picture_image)
    #
    #     Thread(target=_get_all_images).start()
    #     self.root.manager.current = "picturemanager"
    #
    # def push_data2picture_image(self, _):
    #     self.root.manager.ids.picture.ids.rv.data.extend(self.data)
