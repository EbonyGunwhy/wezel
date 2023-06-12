import os
import sys
import venv

# to build an executable of wezel, open the script exec.py and run it it check wezel opens fine
# Then do:
# pyinstaller --name wezel --clean --onefile --noconsole --additional-hooks-dir=. exec.py
# or with splash screen
# pyinstaller --name wezel --clean --onefile --noconsole --additional-hooks-dir=. --splash wezel.jpg exec.py
# When this is done you will find the executable wezel.exe in the folder dist

def post_installation_build_cleanup():
    print("Cleaning up building and compilation files...")
    windows = (sys.platform == "win32") or (sys.platform == "win64") or (os.name == 'nt')
    if windows:
        os.system('move dist\* .')
        os.system('rmdir build /S /Q')
        os.system('rmdir dist /S /Q')
        os.system('del myproject.spec')
        print("Deleting the created Python Virtual Environment for the process...")
        os.system('rmdir .venv /S /Q')
    else:
        os.system('mv dist/* .')
        os.system('rm -rf build/ dist/')
        os.system('rm myproject.spec')
        print("Deleting the created Python Virtual Environment for the process...")
        os.system('rm -r .venv/')

def distribute():
    """Upload new version on PyPI
    
    IMPORTANT! First increment your version number in pyproject.toml:
    - Increment the MAJOR version when you make incompatible API changes.
    - Increment the MINOR version when you add functionality in a backwards compatible manner.
    - Increment the PATCH version when you make backwards compatible bug fixes.

    You need: PyPI username and password
    """

    install()

    os.system(activate() + ' && ' + 'pip install --upgrade build')
    os.system(activate() + ' && ' + 'python -m build')
    os.system(activate() + ' && ' + 'pip install --upgrade twine')
    os.system(activate() + ' && ' + 'twine upload dist/*')

def document():
    """Generate documentation"""

    install()

    path = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(path, 'docs')
    if not os.path.isdir(path):
        os.mkdir(path)

    print('Generating documentation..')
    os.system(activate() + ' && ' + 'pdoc --html -f -c sort_identifiers=False --output-dir ' + str(path) + ' dbdicom')

def activate():
    """Activate virtual environment"""

    venv_dir = os.path.join(os.getcwd(), ".venv")
    os.makedirs(venv_dir, exist_ok=True)
    venv.create(venv_dir, with_pip=True)
    windows = (sys.platform == "win32") or (sys.platform == "win64") or (os.name == 'nt')
    if windows:
        return os.path.join(venv_dir, "Scripts", "activate")
    else: # MacOS and Linux
        return '. "' + os.path.join(venv_dir, "bin", "activate")

def install():
    """Install requirements to a virtual environment"""

    print('Creating virtual environment..')
    os.system('py -3 -m venv .venv')

    print('Installing requirements..')
    os.system(activate() + ' && ' + 'py -m pip install -r requirements.txt')


def build(project, onefile=True, terminal=False, name='my_app', data_folders=[], hidden_modules=[]):
    """Generate project executable"""

    install()
    os.system(activate() + ' && ' + 'pip install pyinstaller')

#    windows = (sys.platform == "win32") or (sys.platform == "win64") or (os.name == 'nt') 

    print('Creating executable..')
    cmd = activate() + ' && ' + 'pyinstaller --name "myproject" --clean'
    #cmd = activate() + ' && ' + 'pyinstaller --name '+ name + ' --clean'
    if onefile: 
        cmd += ' --onefile'
    if not terminal: 
        cmd += ' --noconsole'
    cmd += ' ' + project + '.py'
    os.system(cmd)


if __name__ == '__main__':

    distribute()