from kivy.uix.screenmanager import Screen
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelOneLine


class Setting(Screen):
    def go_menu(self):
        self.manager.current = "menu"

    @staticmethod
    def add_all_rules(rule1, rule2):
        def loop_add_rule(rules):
            for rule in rules.items:
                rules.add_widget(
                    MDExpansionPanel(
                        icon=rules.items[rule],
                        # content=content,
                        panel_cls=MDExpansionPanelOneLine(text=rule),
                    )
                )
        loop_add_rule(rule1)
        loop_add_rule(rule2)


    pass
