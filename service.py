'p4a example service using oscpy to communicate with main application.'
from json import loads
from random import sample, randint
from string import ascii_letters
from time import localtime, asctime, sleep
from oscpy.server import OSCThreadServer
from oscpy.client import OSCClient
from notification import notification
from jnius import autoclass
import requests

CLIENT = OSCClient('localhost', 3001)
PythonService = autoclass('org.kivy.android.PythonService')
PythonService.mService.setAutoRestartService(True)
notify_data = {}


def ping(*_):
    """answer to ping messages"""
    CLIENT.send_message(
        b'/message',
        [
            ''.join(sample(ascii_letters, randint(10, 20)))
                .encode('utf8'),
        ],
    )


def send_date(*args):
    'send date to the application'
    notification.notify(title='testing', message='hey it is working', app_name='nocenstore', ticker='incoming....')
    CLIENT.send_message(
        b'/date',
        [asctime(localtime()).encode('utf8'), ],
    )


def check_notify(data):
    global notify_data
    if data == "None" or loads(data) == notify_data:
        return
    notify_data = loads(data)
    notification.notify(title=notify_data["title"], message=notify_data["message"], app_name='nocenstore',
                        ticker='incoming....', app_icon="assets/logo.png")


if __name__ == '__main__':
    SERVER = OSCThreadServer()
    SERVER.listen('localhost', port=3000, default=True)
    SERVER.bind(b'/ping', ping)
    update = False
    while True:
        try:
            data = requests.get("https://nocenstore.pythonanywhere.com/notificationRoute")
            check_notify(data.text)
        except requests.exceptions.RequestException:
            pass
