'''ASM Common Utilities setup
'''
from setuptools import find_packages, setup

import ASM_utils

setup(
    name='AsmCommon',
    version=ASM_utils.__version__,
    description='Aye-Aye Sensor Node Common',
    author='UC San Diego Engineers for Exploration',
    author_email='e4e@eng.ucsd.edu',
    packages=find_packages(),
    scripts=[],
    install_requires=[
        'tzlocal'
    ],
    extras_require={
        'dev':[
            'pytest',
            'coverage',
            'pylint',
            'wheel',
        ]
    }
)
