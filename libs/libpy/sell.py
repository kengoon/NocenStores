import glob
import os
from threading import Thread
from kivymd.app import MDApp
from kivymd.toast import toast
from plyer import filechooser
from kivy import platform
from kivy.clock import Clock
from kivy.properties import ListProperty
from kivy.uix.screenmanager import Screen


class Sell(Screen):
    images = []
    image_name = []
    data = ListProperty([])
    app = MDApp.get_running_app()

    @staticmethod
    def open_filechooser(instance):
        def call(file_list):
            if not file_list[0]:
                toast("do not select image from gallery, use normal file manager")
                return
            for i in [".png", ".jpg", ".jpeg", ".gif"]:
                if i in file_list[0]:
                    instance.source = file_list[0]
                    return
            if not instance.source:
                toast("please select an image file")
                return

        filechooser.open_file(preview=True, filters=["*.jpg", "*.png", "*.jpeg"], on_selection=call, multiple=True)

    def upload_product_data(self, name, des, price, phone, email, _pic1, _pic2, _pic3):
        instance = [name, des, price, phone, email, _pic1, _pic2, _pic3]
        for data in instance:
            if not data.text:
                toast("please fill all fields")
                return

    def open_gallery(self):
        if self.root.manager.ids.picture.ids.rv.data:
            print("leaving")
            return

        def _get_all_images():
            for dirs, _, files in os.walk("/home/kengo/Pictures" if platform != "android" else "/storage/emulated/0"):
                image_file = glob.glob(f"{dirs}/*.png") + glob.glob(f"{dirs}/*.jpeg") + glob.glob(f"{dirs}/*.jpg")
                for i in image_file:
                    if ("Android/" in i) or (i.startswith(".")):
                        continue
                    self.image_name.append(i.split("/")[-1])
                    self.images.append(os.path.join(dirs, i))
            for image, image_name in zip(self.images, self.image_name):
                self.data.append({"source": image, "text": image_name})
            Clock.schedule_once(self.push_data2picture_image)

        Thread(target=_get_all_images).start()
        self.root.manager.current = "picturemanager"

    def push_data2picture_image(self, _):
        self.root.manager.ids.picture.ids.rv.data.extend(self.data)
