from dbdicom.extensions import sklearn
from wezel.gui import Action, Menu


def if_a_database_is_open(app): 
    return app.database() is not None


def calculate_k_means(app):
    all_series = app.database().series()
    features = app.selected('Series')
    series_labels = [s.label() for s in all_series]
    if features == []:
        features_index = []
        selected = 0
    else:
        features_index = [all_series.index(series) for series in features] 
        selected = features_index[0]
        features_index = features_index[1:]
    cancel, f = app.dialog.input(
        {"label":"Reference feature", "type":"dropdownlist", "list": series_labels, 'value':selected},
        {"label":"Additional features (optional)", "type":"listview", "list": series_labels, 'value':features_index},
        {"label":"Mask", "type":"dropdownlist", "list": ['None'] + series_labels, 'value':0},
        {"label":"Number of clusters", "type":"integer", 'value':2, 'minimum':2}, 
        {"label":"Save clusters in multiple series?", "type":"dropdownlist", "list": ['No', 'Yes'], 'value':0},
        {"label":"Normalize features?", "type":"dropdownlist", "list": ['No', 'Yes'], 'value':1},
        title = "Please select input for K-Means clustering")
    if cancel:
        return
    features = [all_series[f[0]['value']]]
    features += [all_series[i] for i in f[1]['value']]
    if f[2]['value'] == 0:
        mask = None
    else:
        mask = all_series[f[2]['value']-1]
    clusters = sklearn.kmeans(features, mask, n_clusters=f[3]['value'], multiple_series=f[4]['value']==1, normalize=f[5]['value']==1)
    app.display(clusters)
    app.refresh()


def k_means_4d(app):
    all_series = app.database().series()
    features = app.selected('Series')
    series_labels = [s.label() for s in all_series]
    if features == []:
        selected = 0
    else:
        features_index = [all_series.index(series) for series in features] 
        selected = features_index[0]
    cancel, f = app.dialog.input(
        {"label":"Features (4D)", "type":"dropdownlist", "list": series_labels, 'value':selected},
        {"label":"Mask", "type":"dropdownlist", "list": ['None'] + series_labels, 'value':0},
        {"label":"Number of clusters", "type":"integer", 'value':2, 'minimum':2}, 
        {"label":"Save clusters in multiple series?", "type":"dropdownlist", "list": ['No', 'Yes'], 'value':0},
        {"label":"Normalize features?", "type":"dropdownlist", "list": ['No', 'Yes'], 'value':1},
        title = "Please select input for K-Means clustering")
    if cancel:
        return
    features = all_series[f[0]['value']]
    if f[1]['value'] == 0:
        mask = None
    else:
        mask = all_series[f[1]['value']-1]
    clusters = sklearn.kmeans_4d(features, mask, n_clusters=f[2]['value'], multiple_series=f[3]['value']==1, normalize=f[4]['value']==1)
    app.display(clusters)
    app.refresh()



def calculate_sequential_k_means(app):
    all_series = app.database().series()
    features = app.selected('Series')
    series_labels = [s.label() for s in all_series]
    if features == []:
        features_index = []
        selected = 0
    else:
        features_index = [all_series.index(series) for series in features] 
        selected = features_index[0]
        features_index = features_index[1:]
    cancel, f = app.dialog.input(
        {"label":"Reference feature", "type":"dropdownlist", "list": series_labels, 'value':selected},
        {"label":"Additional features (optional)", "type":"listview", "list": series_labels, 'value':features_index},
        {"label":"Mask", "type":"dropdownlist", "list": ['None'] + series_labels, 'value':0},
        {"label":"Number of clusters (each iteration)", "type":"integer", 'value':2, 'minimum':2}, 
        {"label":"Save clusters in multiple series?", "type":"dropdownlist", "list": ['No', 'Yes'], 'value':1},
        title = "Please select input for sequential K-Means clustering")
    if cancel:
        return
    features = [all_series[f[0]['value']]]
    features += [all_series[i] for i in f[1]['value']]
    if f[2]['value'] == 0:
        mask = None
    else:
        mask = all_series[f[2]['value']-1]
    clusters = sklearn.sequential_kmeans(features, mask, n_clusters=f[3]['value'], multiple_series=f[4]['value']==1)
    app.display(clusters)
    app.refresh()



action_k_means = Action('K-Means clustering', on_clicked=calculate_k_means, is_clickable=if_a_database_is_open)
action_sequential_k_means = Action('K-Means clustering (sequential)', on_clicked=calculate_sequential_k_means, is_clickable=if_a_database_is_open)
action_k_means_4d = Action('K-Means clustering (time series)', on_clicked=k_means_4d, is_clickable=if_a_database_is_open)


menu_all = Menu('sklearn')
menu_all.add(action_k_means)
menu_all.add(action_sequential_k_means)
menu_all.add(action_k_means_4d)