from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="switchbot2mqtt",
    packages=["switchbot2mqtt"],
    version="0.0.1",
    license="GPLv3",
    description="Control your Switchbot device using MQTT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Martijn Versluis",
    author_email="martijnversluis@users.noreply.github.com",
    url="https://github.com/martijnversluis/switchbot2mqtt",
    keywords=["Switchbot", "MQTT"],
    install_requires=["switchbotpy", "paho-mqtt"],
)
