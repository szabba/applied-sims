#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

from setuptools import setup

setup(
    name='applied-sims',
    version='0.1',
    classifiers=[
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Physics',
        'Intended Audience :: Other Audience',
    ],
    install_requires=['numpy >=1.9.1,<2'],
    packages=['polymer_states'],
    url='http://github.com/szabba/applied-sims',
    license='MPL-2.0',
    author='Karol Marcjan',
    author_email='karol.marcjan@gmail.com',
    description=''
)
