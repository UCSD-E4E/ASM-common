from setuptools import setup, find_packages
import os
import ASM_utils

setup(
    name='SensorNode',
    version=ASM_utils.__version__,
    description='Sensor Node',
    author='UC San Diego Engineers for Exploration',
    author_email='e4e@eng.ucsd.edu',
    packages=find_packages(),
    scripts=[],
    install_requires=[
    ]
)
