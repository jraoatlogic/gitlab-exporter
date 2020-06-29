import setuptools
from src.gitlab_exporter.helpers import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "gitlab-exporter",
    version = __version__,
    author = "Axel Duerkop",
    author_email = "axel.duerkop@tuhh.de",
    description = "Export various data sets from GitLab issues, projects and groups",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://collaborating.tuhh.de/hos/modernes-publizieren/offen/software/middleware/gitlab-exporter",
    packages = setuptools.find_packages(where = 'src'),
    python_requires = ">=3.6",
    py_modules = ['api'],
    package_dir = {
        '': 'src'
    },
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    entry_points = {
        'console_scripts': [
            'gitlab-exporter=gitlab_exporter.api:main',
        ],
    },
    install_requires = [
        'astroid>=2.1.0',
        'certifi>=2018.11.29',
        'chardet>=3.0.4',
        'icalendar>=4.0.3',
        'idna>=2.8',
        'isort>=4.3.4',
        'lazy-object-proxy>=1.3.1',
        'mccabe>=0.6.1',
        'numpy>=1.16.1',
        'pandas>=0.24.1',
        'ply>=3.11',
        'pypandoc>=1.4',
        'python-dateutil>=2.8.0',
        'python-gitlab>=1.7.0',
        'pytz>=2018.9',
        'requests>=2.21.0',
        'six>=1.12.0',
        'typed-ast>=1.3.1',
        'urllib3>=1.24.1',
        'wrapt>=1.11.1'
    ]
)