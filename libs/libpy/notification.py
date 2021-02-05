from kivy.uix.screenmanager import Screen


class Notification(Screen):
    update = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = [{"text": "sdsjdhjshdjsh dksdjskdjslds s;dsld;lsd;ls  lds;dd dpfdfpodpf d"},
                     {"text": "sdsjdhjshdjsh dksdjskdjslds s;dsld;lsd;ls  lds;d"},
                     {"text": "sdsjdhjshdjsh dksdjskdjslds s;dsld;lsd;ls  lds;d"},
                     {"text": "sdsjdhjshdjsh dksdjskdjslds s;dsld;lsd;ls  lds;d"},
                     {"text": "sdsjdhjshdjsh dksdjskdjslds s;dsld;lsd;ls  lds;d"},
                     {"text": "sdsjdhjshdjsh dksdjskdjslds s;dsld;lsd;ls  lds;d"},
                     {"text": "sdsjdhjshdjsh dksdjskdjslds s;dsld;lsd;ls  lds;d"},
                     {"text": "sdsjdhjshdjsh dksdjskdjslds s;dsld;lsd;ls  lds;d"},
                     {"text": "sdsjdhjshdjsh dksdjskdjslds s;dsld;lsd;ls  lds;d"},
                     {"text": "sdsjdhjshdjsh dksdjskdjslds s;dsld;lsd;ls  lds;d"}]

    def on_enter(self, *args):
        if not self.update:
            for data in self.data:
                self.ids.rv.data.append(data)
                self.update = True

    def go_home(self):
        self.manager.current = "home"
