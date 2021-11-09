def check_add_widget(app, var, root, factory_widget, ids): # NOQA
    if not eval(f"app.{var}"):
        widget = factory_widget
        try:
            root.manager.add_widget(widget)
            root.manager.ids[ids] = widget
        except AttributeError:
            root.root.add_widget(widget)
            root.root.ids[ids] = widget
        exec(f"app.{var} = True")
