from kivy.uix.screenmanager import Screen


class Used(Screen):
    update = False
    menu = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = [{"source": "assets/7.jpg", "product_price": 1000, "product_name": "crab"},
                     {"source": "assets/9.jpg", "product_price": 34500, "product_name": "house"},
                     {"source": "assets/10.jpg", "product_price": 1000, "product_name": "crane"},
                     {"source": "assets/11.jpg", "product_price": 22431000, "product_name": "Mansion"},
                     {"source": "assets/12.jpg", "product_price": 1000, "product_name": "crab"},
                     {"source": "assets/13.jpg", "product_price": 1000, "product_name": "crab"},
                     {"source": "assets/14.jpg", "product_price": 1000, "product_name": "crab"},
                     {"source": "assets/15.jpg", "product_price": 1000, "product_name": "crab"},
                     {"source": "assets/16.jpg", "product_price": 1000, "product_name": "crab"},
                     {"source": "assets/7.jpg", "product_price": 1000, "product_name": "crab"},
                     {"source": "assets/9.jpg", "product_price": 34500, "product_name": "house"},
                     {"source": "assets/10.jpg", "product_price": 1000, "product_name": "crane"},
                     {"source": "assets/11.jpg", "product_price": 22431000, "product_name": "Mansion"},
                     {"source": "assets/12.jpg", "product_price": 1000, "product_name": "crab"},
                     {"source": "assets/13.jpg", "product_price": 1000, "product_name": "crab"},
                     {"source": "assets/14.jpg", "product_price": 1000, "product_name": "crab"},
                     {"source": "assets/15.jpg", "product_price": 1000, "product_name": "crab"},
                     {"source": "assets/16.jpg", "product_price": 1000, "product_name": "crab"},
                     {"source": "assets/15.jpg", "product_price": 1000, "product_name": "crab"},
                     {"source": "assets/16.jpg", "product_price": 1000, "product_name": "crab"}
                     ]

    def on_enter(self, *args):
        if not self.update:
            for data in self.data:
                self.ids.rv.data.append(data)
            self.update = True

    pass
