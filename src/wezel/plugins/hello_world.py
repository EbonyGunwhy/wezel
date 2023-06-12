from wezel.gui import Menu, Action


def say_hello_world(app):
    app.dialog.information("Hello World!", title='Hello world plugin')

def say_hello_universe(app):
    app.dialog.information("Hello Universe!", title='Hello world plugin')

def say_hello_database(app):
    app.dialog.information("Hello Database!", title='Hello world plugin')

def say_hello_england(app):
    app.dialog.information("Hello England!", title='Hello world plugin')

def say_hello_scotland(app):
    app.dialog.information("Hello Scotland!", title='Hello world plugin')

def say_hello_wales(app):
    app.dialog.information("Hello Wales!", title='Hello world plugin')

def say_hello_n_ireland(app):
    app.dialog.information("Hello Northern Ireland!", title='Hello world plugin')

def say_hello(app, who='World'):
    app.dialog.information('Hello ' + who +'!', title='Hello world plugin')

def say_hello_australia(app):
    app.dialog.information("G'day mate!", title='Hello world plugin')


def when_a_database_is_open(app):
    return app.database() is not None 





# Menu distributed as part of the plugin

menu = Menu('Hello')
menu.add_action('Hello World', on_clicked=say_hello_world)
menu.add_action('Hello Universe', on_clicked=say_hello_universe)
menu.add_action('Hello Database', on_clicked=say_hello_database, is_clickable=when_a_database_is_open)
menu.add_separator()
menu_uk = menu.add_menu('Hello UK')
menu_uk.add_action('Hello England', on_clicked=say_hello_england)
menu_uk.add_action('Hello Scotland', on_clicked=say_hello_scotland)
menu_uk.add_action('Hello Wales', on_clicked=say_hello_wales)
menu_uk.add_action('Hello Northern Ireland', on_clicked=say_hello_n_ireland)
menu.add_separator()
menu_uni = menu.add_menu('Hello Neighbours')
menu_uni.add_action('Hello Ireland', on_clicked=lambda app: say_hello(app, 'Ireland'))
menu_uni.add_action('Hello France', on_clicked=lambda app: say_hello(app, 'France'))
menu_uni.add_action('Hello Germany', on_clicked=lambda app: say_hello(app, 'Germany'))
menu_uni.add_action('Hello Belgium', on_clicked=lambda app: say_hello(app, 'Belgium'))
menu.add_separator()
menu.add_action('Hello Australia', on_clicked=say_hello_australia)


# Actions that are distributed as part of the plugin

hello_japan = Action('Hello Japan', on_clicked=lambda app: say_hello(app, 'Japan'))
hello_china = Action('Hello China', on_clicked=lambda app: say_hello(app, 'China'))