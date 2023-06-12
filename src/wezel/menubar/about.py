import webbrowser
from wezel import icons
from wezel.gui import Menu, Action


def about_wezel(app):
    webbrowser.open("https://github.com/QIB-Sheffield/wezel")

def about_fugue(app):
    webbrowser.open("https://p.yusukekamiyamane.com/")



action_about_wezel = Action('Wezel', on_clicked=about_wezel, icon=icons.wezel_icon_transparent)
action_about_fugue = Action('Fugue icons', on_clicked=about_fugue)


menu = Menu('About')
menu.add(action_about_wezel)
menu.add(action_about_fugue)
