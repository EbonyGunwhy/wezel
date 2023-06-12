***DRAFT README - oudated content***

`wezel` is a Python toolbox for prototyping medical imaging applications. 



# How can I use existing `wezel` applications?

You can use `wezel` applications to visualise and analyse medical images, using a standard graphical interface much like any other medical image viewer. 

To try this out, download an example application (coming soon), then double-click the file to start - no software installation required. 

If you are working on a specific project, you may have been given a `wezel` application directly by a collaborator, or perhaps you found one online or as supplementary material with a publication. 

Some video tutorials are provided (**coming soon**) to illustrate the use of the graphical interface. The rest of this document provides detail for application developers. 

# How can I develop new `wezel` applications?

If you are a developer of new applications, you can use `wezel` to prototype and test your application. Once you are happy with the result, `wezel` can generate an executable which you can pass on to analysts or other users. 

`wezel` is distributed under an open license so you can make the executable and/or the source code publicly available, for instance as supplementary material 
in publications. 

## Installing wezel

Run `pip install wezel`

## Customizing `wezel`: menus and apps

To run `wezel` in a script, import the package, 
launch a new application and show it to the user:

```python
import wezel

wsl = wezel.app()      # launch an application
wsl.show()              # show the application
```

This will launch a dummy version of `wezel` without any functionality. 

The easiest way to customize `wezel` is by replacing the menubar with a custom made one. For instance, try setting the `hello_world` menu included in the `wezel` distribution: 

```python
import wezel

wsl = wezel.app()                   # launch an application
wsl.set_menu(wezel.menus.hello_world)      # set a custom menu
wsl.show()                          # show the application
```

Of course in practice you will be running your own menus. For instance, assume you have created a package `foo` which contains a menu definition of your own:

```python
import wezel
import foo

wsl = wezel.app()                  # launch an application
wsl.set_menu(foo.mymenu)        # set a custom menu
wsl.show()                          # show the application
```

A more useful application is the dicom.Windows app included in the `wezel` distribution. To run it, just set a different app:

```python
import wezel

wsl = wezel.app()           # launch an application
wsl.set_app(wezel.apps.dicom.Windows)     # set a custom app
wsl.show()                   # show the application
```

Wezel also includes an app for visualising and manipulating numpy arrays (**coming soon!**):

```python
import wezel

wsl = wezel.app()           # launch an application
wsl.set_app(wezel.apps.numpy)     # set a custom app
wsl.show()                   # show the application
```

When launched in this way a window will pop up allowing the 
user the select a dataset from disk. You can also set data interactively. Try this out by visualising an empty a 4-dimensional array:

```python
import numpy as np
import wezel

wsl = wezel.app()           # launch an application
wsl.set_app(wezel.apps.numpy)     # set a custom app
wsl.set_data(np.empty((10, 20, 5, 12)))
wsl.show()                   # show the application
array = wsl.get_data()
```

When calling `show()` the program halts until the user closes the window. Typically the user will have manipulated the array using the app. As shown in the example, the result can be retrieved with `get_data()`.

The tutorial contains a few other simple applications, 
but of course you may have written your own. For instance, say you have a package `foo` that contains an app:

```python
import wezel
import foo

wsl = wezel.app()                # launch an application
wsl.set_app(foo.myapp)        # set a custom app
wsl.show()                        # show the application
```

See below for some examples of how apps can be defined.

## Writing custom `wezel` menus

A menu on the `wezel` menu bar is effectively a list of menu buttons, or "actions" as they are called. Formally it is defined as a function which takes a parent menu or the menubar itself as argument. For instance, the Hello World menu inserted in the example above is defined as follows:

```python
def hello_world(parent):
    hello = parent.menu('Hello')
    hello.action(HelloWorld, text="Hello World")
```

As the example shows, a submenu of any parent menu can be created by calling `parent.menu(label)`, where `label` is the text on the menu button. 

Then an action can be created in any menu by calling `parent.action()` where the first argument defines the action (see below) and the (optional) `text` argument defines the text that will be shown on the button.  

More complicated menus including submenus can be created in the same way. For instance the following adds a second `HelloWorld` action and a submenu which has two other `HelloWorld` actions:

```python
def hello_world_sub(parent):
    hello = parent.menu('Hello')
    hello.action(HelloWorld, text="Hello World")
    hello.action(HelloWorld, text="Hello World (again)")
    subMenu = hello.menu('Submenu')
    subMenu.action(HelloWorld, text="Hello World (And again)")
    subMenu.action(HelloWorld, text="Hello World (And again!)")
```

You can try running this to see how it looks:

```python
import wezel

wsl = wezel.app()              # launch an application
wsl.set_menu(hello_world_sub)   # set a custom menu
wsl.show()                      # show the application
```

## Writing `wezel` actions

`HelloWorld` as used above is an example of an action. When the user clicks on it, a window pops up carrying a title 'My first action!' and saying "Hello World!". 
The program is paused until the user closes the pop-up. 
The `HelloWorld` action is defied as follows:

```python
import wezel

class HelloWorld(wezel.gui.Action):

    def run(self, app):
        app.dialog.information("Hello World!", title='My first action!')
```

As the example shows, all actions in `wezel` must be defined by subclassing the `wezel.gui.Action` class. There are no other compulsory arguments, so the following creates a functional action which does absolutely nothing when clicked:

```python
import wezel

class DoNothing(wezel.gui.Action):
    pass
```

If the `run()` function is specified, it is executed when the user clickes the menu button corresponding to the action. Apart from `self`, `run()` has a compulsory argument `app` which gives access to other relevant functionality. In the case of `HelloWorld` this is 
the dialog class which has some options for launching pop-up windows. 

## Creating `wezel` executables

`wezel` applications mean nothing without a simple way of distributing them as an executable, which can be run without the need for other installations by a simply mouse click. `wezel` has some built-in functionality for creating 
executables. As an example, imagine you have created the hello world script above:

```python
import wezel
import mystuff

wsl = wezel.app()                # launch an application
wsl.set_app(mystuff.myapp)        # set a custom app
wsl.show()                        # show the application
```

In order to generate an executable, save the script in a separate file, for instance "myproject.py". You can generate an executable by calling the `build` function of `wezel` (**coming soon!**):

```python
import wezel
wezel.build('myproject')
```

This must be executed from the same folder as myproject.py - as a script or interactively. After completion you will find a single file `wezel.exe` which you can distribute to the users if your applications. They will not 
need to install anything else - just double-click and run. 

If your project contains dependencies on other external packages, then these must be detailed in a text file "requirements.txt" as is customary for Python projects. The build function will install these along with 
`wezel`'s own dependencies. The requirements.txt file must be located in the same folder as pyproject.py.

If your project contains additional data such as images, icons or other types of files, the folders that contain these data must be provided as an additional argument to `build()`, as a list of one or more paths:

```python
impor os
import wezel

wezel.build('myproject', 
    data_folders = ['myimages', os.path.join('mytables','parameters')],
    )
```

By default the build function generates a single .exe file. As `wezel` is a graphical interface application this will not launch a terminal when the .exe file is opened. These settings are most practical for external users but for debugging purposes the terminal and a multi-file build can be more convenient. These can be created by setting the `onefile` and `terminal` keywords to `False` and `True`, 
respectively:

```python
import wezel
wezel.build('myproject', 
    data_folders = ['myimages', os.path.join('mytables','parameters')],
    terminal = True, 
    onefile = False,
    )
```

(...) Support for hidden imports and collect data


## Creating `wezel` apps

The graphical user interface of `wezel` is built on PyQt's 
[QMainWindow](https://doc.qt.io/qt-5/qmainwindow.html#details), and always has a menu bar (top), a status bar (bottom), and a central widget. Applications may also use toolbars and dockwidgets if appropriate.

A `wezel` app is a class that manages the content of these different components, coordinates between them and holds the data currently managed by `wezel`. In addition any `wezel` app has access to some convenience classes, such as the dialog class and progress bar which provides a convenient programming interface for common interactions with the user.

An example of a very simple (and not very useful!) `wezel` app is the `About` app which can be found in the `welcome` module of the default 
`wezel.apps`:

```python
import wezel

class WezelAbout(wezel.App):             # Required: subclass core.App
    def __init__(self, wzl):     # Required: initialize core.App                       
        super().__init__(wzl)    #    with instance of `Wezel`

        self.set_central(ImageLabel())          # set the central widget
        self.set_menu(menu)                     # set the menu
        self.set_status("Welcome to Wezel!")   # display message in status bar
```

Apps can be changed at runtime - for instance the following action will toggle between the About and Windows apps:

```python
import wezel

class ToggleApp(wezel.gui.Action):

    def run(self, app):
        
        wzl = app.wezel
        if app.__class__.__name__ == 'About':
            wzl.app = wezel.apps.dicom.Windows(wzl)
        elif app.__class__.__name__ == 'Windows':
            wzl.app = wezel.apps.welcome.About(wzl)
```

# How can I contribute to `wezel`?

**Coming soon**

# About `wezel`

`wezel` is a Python environment for prototyping and deploying 
quantitative medical imaging (qMRI) applications. 

Method development in qMRI is hampered by a gap between scientists 
who work with scripts or in command-line mode, 
and end-users who rely on graphical user interfaces. 
`wezel` aims to bridge that gap by providing an easy way 
to integrate pipeline scripts in an existing graphical interface 
environment that interfaces with DICOM databases 
and can be passed on to clinical users. 

The aim is to enable a rapid feedback loop between development 
and application under real-world conditions, 
and streamline the deployment of novel methods into clinical trials. 

## Background

Efficient, integrated product development involves an iterative 
process of building prototypes to test the basic ideas under 
real-world conditions as early as possible in the product development lifecycle, 
subsequently revising the concepts and ideas on the basis of 
this experience, and producing improved prototypes that can 
be tested under the same conditions again. This creates a 
rapid feedback loop between development and application that 
allows to intercept design flaws at an early stage and avoids 
expensive and late-stage failures of novel concepts. 

Applied sciences such as quantitative MRI can benefit from 
an integrated product development approach, as a way of 
steering the basic research and method development in the 
direction most likely to produce functional real-world 
applications. In practice this is often difficult due to 
the significant overhead required in moving from a set of 
command-line tools operating on computantionally convenient 
image dataformats (nifty, numpy), to a tool that can be applied 
by clinical end users on clinical (DICOM) data in a clinical 
environment. 

Highly successful open source software tools such 
as 3D Slicer or MITK are going a long way towards bridging this 
gap, but integrating simple scripts with novel image processing 
pipelines into these environments still presents a daunting task 
to basic scientists without the necessary computer science background.

`wezel` aims to reduce the gap between development and 
application of novel qMRI methods by significantly reducing the 
overhead required to integrate novel pipelines into a software 
environment suitable for clinical users working on clinical data. 
It is envisioned that this will speed up the translation of new 
methods into clinical research, and increase the value of clinical 
research by facilitating the integration of novel imaging biomarkers 
as secondary endpoints.

## Description

`wezel` is freely available via www.wezel.pro, is designed for 
open science and therefore entirely written in Python 3 and 
released under an open Apache 2.0 license. 

Since clinical data always ultimately arrive to the developer 
and the clinical end user alike in the form of DICOM images, 
`wezel` includes a DICOM read/write programming interface. 
The idea of this interface is to hide the complexity and inaccessible 
bureaucracy of the DICOM format from the scientist writing in Python, 
instead providing DICOM read and write access using more intuitive 
concepts such as folder structures, array slicing operations and 
class attributes. This allows the developer to prototype their new 
methods straight into DICOM, entirely removing a feared barrier to 
deployment of novel image processing pipelines in clinical studies: 
the need to convert pipelines interfacing with scientific data formats 
into pipelines interfacing with DICOM. 

The second important barrier to clinical translation is the need to 
interface command-line scripts with graphical user interfaces 
allowing user intervention such as drawing or editing regions 
of interest, or performing visual quality control of medical images. 
Graphical interfaces follow an event-drive logic that is often 
unfamiliar the basic scientist and involves a steep learning 
curve that is often prohibitive, resulting in prototypes that 
are difficult to access by clinical users and do not imitate 
the conditions under which these tools will ultimately be deployed. 

Wezel aims to address this challenge by providing a number 
of prepackaged graphical user interfaces with clear programming 
interfaces that enable the integration of user-defined image 
processing pipelines with a simple and intuitive commands similar 
to the print or display commands typically accessed in command-line. 
Using this approach, developers can easily configure Wezel by 
creating customized menus and compiling those to create 
applications that can be distributed to clinical collaborators 
as independent Wezel apps. 

An expanding library of graphical user 
interface elements (widgets) for setting and accessing DICOM objects 
is also available to support the development of customised GUIs.
Wezel deployment will be supported by well-documented code base and 
a series of user-friendly tutorials for clinical users.

## Applications of `wezel`

`wezel` development is jointly supported by the TRISTAN project 
funded by the Innovative Medicines Initiative (https://www.imi-tristan.eu/) 
and the UKRIN-MAPS project funded by the UK's Medical Research Council 
(https://www.nottingham.ac.uk/research/groups/spmic/research/uk-renal-imaging-network/ukrin-maps.aspx).

### TRISTAN

The TRISTAN project aims to develop imaging biomarkers for drug toxicity. 
Wezel is developed by the TRISTAN work package 2 on imaging 
biomarkers for drug toxicity, and will form the vehicle to 
distribute an imaging biomarker assay for predicting drug-drug 
interactions and liver toxicity. 

The food and drug administration 
(FDA) has accepted a biomarker qualification letter of intent 
describing the assay (https://www.fda.gov/media/149415/download) 
and evidence is currently being collected to support a full 
application for biomarker qualification. While a commercial 
assay will be taken forward by a collaborating company, Wezel 
will be offered as a free service along with supporting data 
and SOPs for those interested to replicate the assay locally. 

### UKRIN-MAPS and AFiRM

The UKRIN-MAPS project provides the technical underpinnings for 
a standardised multi-vendor approach to quantitative renal MRI. 
It is a collaborative UK-based project led by Nottingham 
University with support from 3 main MRI vendors. A set of 
standardised quantitative MRI protocols has been developed 
and is currently being validated in travelling volunteer studies. 
Basic analysis algorithms are available via an open access 
library (https://github.com/UKRIN-MAPS/ukat) and these are 
currently being wrapped up into Wezel for deployment into 
clinical trials. 

One clinical trial, the AFiRM study, will use 
these methods and has started recruiting in 2021. AFiRM will 
ultimately recruit 500 patients with Chronic Kidney Disease 
who will have 2 multi-parametric protocols 2- years apart. 
Analysis and QC of all data will be performed in Wezel and 
functional pipelines have already been tested on the first datasets. 

## Current `wezel` version

Wezel is currently at a prototype version that has not been
tried and tested under the defined context of use. 
First applications in 4 multi-centre renal and liver projects 
are currently underway. Until these applications have 
progressed to their first endpoints, wezel is considered an 
early prototype still subject to substantial change in the code base and documenting material. 

## Acknowledgement

Ferret brain image from https://www.med.unc.edu/bric/camri/imaging-service/3d-t2w-mri-of-the-ferret-brain/