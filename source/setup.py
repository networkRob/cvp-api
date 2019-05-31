from setuptools import setup

setup(name="rcvp_api",
    version="1.2",
    description="Module to interact with Arista CloudVision",
    url="https://github.com/networkRob/cvp-api",
    author="Rob Martin",
    author_email="robmartin@arista.com",
    packages=['rcvp_api'],
    install_requires=[
        'requests'
    ],
    zip_safe=False)