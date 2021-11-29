from kivy import platform

SERVICE_NAME = u'{packagename}.Service{servicename}'.format(
    packagename=u'org.mindset.nocenstore.nocenstore',
    servicename=u'Notification'
)


def check_add_widget(app, var, root, factory_widget, ids):  # NOQA
    if not eval(f"app.{var}"):
        from kivy.factory import Factory  # NOQA
        widget = eval(factory_widget)
        try:
            root.manager.add_widget(widget)
            root.manager.ids[ids] = widget
        except AttributeError:
            root.root.add_widget(widget)
            root.root.ids[ids] = widget
        exec(f"app.{var} = True")


def start_service():
    if platform == 'android':
        from jnius import autoclass
        service = autoclass(SERVICE_NAME)
        mActivity = autoclass(u'org.kivy.android.PythonActivity').mActivity
        argument = ''
        service.start(mActivity, argument)

    elif platform in ('linux', 'linux2', 'macos', 'win'):
        from runpy import run_path
        from threading import Thread
        service = Thread(
            target=run_path,
            args=['service.py'],
            kwargs={'run_name': '__main__'},
            daemon=True
        )
        service.start()
    else:
        raise NotImplementedError(
            "service start not implemented on this platform"
        )
