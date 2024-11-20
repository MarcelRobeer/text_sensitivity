from distutils.util import convert_path
from os import path

import setuptools

main_ns = {}
with open(convert_path('text_sensitivity/_version.py')) as ver_file:
    exec(ver_file.read(), main_ns)

with open(path.join(path.abspath(path.dirname(__file__)), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup( # type: ignore
    name = 'text_sensitivity',
    version = main_ns['__version__'],
    description = 'Extension of text_explainability for sensitivity testing (robustness, fairness, safety)',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    author = 'Marcel Robeer',
    author_email = 'm.j.robeer@uu.nl',
    license = 'GNU LGPL v3',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Topic :: Scientific/Engineering :: Artificial Intelligence'
    ],
    url = 'https://github.com/MarcelRobeer/text_sensitivity',
    packages = setuptools.find_packages(), # type : ignore
    include_package_data = True,
    install_requires = [
        'genbase>=0.2.14',
        'text-explainability>=0.6.5',
        'nlpaug>=1.1.3',
        'Faker>=9.2.0',
        'yaspin>=0.15.0',
    ],
    python_requires = '>=3.8'
)
