import sys
import subprocess


def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


install('requests')
install('selenium')
install('webdriver_manager')
