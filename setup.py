from setuptools import setup, find_packages

setup(
    name="helper",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pyperclip>=1.11.0",
        "pywin32>=306; sys_platform == 'win32'",
        "requests>=2.32.5",
        "rich>=14.2.0",
        "urllib3>=1.26.0,<3.0.0",
    ],
)
