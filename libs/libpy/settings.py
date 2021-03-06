from kivy.uix.screenmanager import Screen
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelOneLine


class Setting(Screen):
    def go_home(self):
        self.manager.current = "home"

    @staticmethod
    def add_all_rules(rule1, rule2):
        def loop_add_rule(rules, id):
            for index, rule in enumerate(rules.items):
                rules.add_widget(
                    MDExpansionPanel(
                        icon=rules.items[rule],
                        content=rules.content[index],
                        panel_cls=MDExpansionPanelOneLine(text=rule),
                    )
                )
                rules.ids[f"_{id}{index}"] = rules.children[0]
        loop_add_rule(rule1, "r1")
        loop_add_rule(rule2, "r2")
