import os
from json import loads, dumps
from os.path import exists
from threading import Thread
from kvdroid import platform
from oscpy.server import OSCThreadServer
from oscpy.client import OSCClient
from jnius import autoclass

if exists("tmp"):
    import shutil

    shutil.rmtree("tmp")
    os.mkdir("tmp")

CLIENT = OSCClient('localhost', 3001)
MAX_IMAGE_SIZE = 150
server = OSCThreadServer()
server.listen('localhost', port=3009, default=True)
print("Service: server initiated")
if platform == "android":
    PythonService = autoclass('org.kivy.android.PythonService')
    PythonService.mService.setAutoRestartService(True)
    from kvdroid.jimplement import get_resource
    from kvdroid.jclass.android.graphics import Color
    from kvdroid.jimplement.notification import create_notification


@server.address(b"/receive_data")
def receive_data(message: bytes):
    json_data = loads(message.decode("utf8"))
    Thread(target=get_raw_image, args=(*json_data,)).start()


def get_raw_image(data_dic, index, path):
    import requests
    while True:
        from PIL import Image
        try:
            response = requests.get(data_dic["imagePath"], stream=True)
            response.raw.decode_content = True
            im = Image.open(response.raw).convert("RGB")
            if im.size[0] > MAX_IMAGE_SIZE or im.size > MAX_IMAGE_SIZE:
                im = im.resize((int(im.size[0]/4), int(im.size[1]/4)), Image.ANTIALIAS)
            im.save(f"tmp/{path}/{index}.jpg")
            data_dic["source"] = f"tmp/{path}/{index}.jpg"
            bytes_data = dumps([data_dic, path]).encode("utf8")
            if path == "home":
                CLIENT.send_message(b"/update_trending_product", [bytes_data])
            elif path == "used":
                CLIENT.send_message(b"/update_used_product", [bytes_data])
            else:
                CLIENT.send_message(b"/update_category_product", [bytes_data])
            return
        except requests.exceptions.RequestException:
            pass


def send_date(*args):
    pass


def main():
    import requests
    from kvdroid.jclass.java.net import URL
    from jnius import JavaException
    notify_data = {}
    channel_id = 0
    large_stream = None
    big_stream = None
    while True:
        if platform == "android":
            print("Service: Running")
            try:
                data = requests.get("https://nocenstore.pythonanywhere.com/notificationRoute")
                if data.text == "None" or loads(data.text) == notify_data:
                    continue
                notify_data: dict = loads(data.text)
                if notify_data.get("big_picture", False):
                    url = URL(notify_data["big_picture"])
                    connection = url.openConnection()
                    connection.setDoInput(True)
                    connection.connect()
                    big_stream = connection.getInputStream()
                if notify_data.get("large_icon", False):
                    url = URL(notify_data["large_icon"])
                    connection = url.openConnection()
                    connection.setDoInput(True)
                    connection.connect()
                    large_stream = connection.getInputStream()
                create_notification(
                    small_icon=get_resource("drawable").ic_nocenstore,
                    channel_id=f"{channel_id}", title=notify_data["title"],
                    text=notify_data["message"], ids=channel_id, channel_name=f"ch{channel_id}",
                    large_icon=
                    "assets/logo.png" if not large_stream else large_stream,
                    small_icon_color=Color.rgb(0x00, 0xC8, 0x53),
                    expandable=True,
                    big_picture="assets/ico.png" if not big_stream else big_stream,
                    set_large_icon=True
                )
                channel_id += 1
            except (requests.exceptions.RequestException, JavaException) as error:
                print(f"Encountered Error: {error}")


if __name__ == '__main__':
    update = False
    main()
