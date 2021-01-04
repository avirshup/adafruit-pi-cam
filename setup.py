import versioneer
from setuptools import setup, find_packages

setup(
    name="adafruit_picam",
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=[
        "attrs~=20.3.0",
        "cattrs~=1.1.2",
        "click~=7.1.2",
        "evdev~=1.3.0",
        "picamera~=1.13",
        "pygame~=1.9.4",
        "sortedcontainers~=2.3.0",
    ],
    package_data={"adafruit_picam": ["icons/*"]},
    include_package_data=True,
    license="BSD-2-Clause",
    description="Adafruit pi camera, updated for python 3",
    use_scm_version=True,
    cmdclass=versioneer.get_cmdclass(),
    entry_points={"console_scripts": ["adapicam=adafruit_picam.main:entrypoint"]},
)
