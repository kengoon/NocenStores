from kivy.uix.screenmanager import Screen


class Feeds(Screen):
    update = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = [
            {"store": "test", "product_name": "ksjdksdjksjd", "product_price": 1020232, "source": "assets/0.jpg"},
            {"store": "test", "product_name": "ksjdksdjksjd", "product_price": 1020232, "source": "assets/0.jpg"},
            {"store": "test", "product_name": "ksjdksdjksjd", "product_price": 1020232, "source": "assets/0.jpg"},
            {"store": "test", "product_name": "ksjdksdjksjd", "product_price": 1020232, "source": "assets/0.jpg"},
            {"store": "test", "product_name": "ksjdksdjksjd", "product_price": 1020232, "source": "assets/0.jpg"},
            {"store": "test", "product_name": "ksjdksdjksjd", "product_price": 1020232, "source": "assets/0.jpg"},
            {"store": "test", "product_name": "ksjdksdjksjd", "product_price": 1020232, "source": "assets/0.jpg"}
        ]

    def on_enter(self, *args):
        if not self.update:
            for data in self.data:
                self.ids.rv.data.append(data)
            self.update = True
