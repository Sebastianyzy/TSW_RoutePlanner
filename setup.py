import sys
import subprocess

# pip install packages


def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


def main():
    install('requests')
    install('selenium')
    install('webdriver_manager')


if __name__ == "__main__":
    main()
