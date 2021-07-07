# -*- coding: utf-8 -*-
from os import path
from os import sep

import setuptools

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.rst"), encoding="utf-8") as f:
    readme = f.read()

with open("requirements.txt") as f:
    required = f.read().splitlines()

setup_requirements = [
    "setuptools_scm",
    "pytest-runner",
]

test_requirements = [
    "pytest>=3",
]

about = {}
with open(
    path.join(here, "planet_crs_registry", "_version.py"),
    encoding="utf-8",
) as f:
    exec(f.read(), about)

setuptools.setup(
    use_scm_version=True,
    name=about["__name_soft__"],
    description=about["__description__"],
    long_description=readme,
    author=about["__author__"],
    author_email=about["__author_email__"],
    url=about["__url__"],
    license=about["__license__"],
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    package_data={
        'about["__name_soft__"]': ["logging.conf"],
    },
    include_package_data=True,
    data_files=[
        (
            "templates",
            [
                "templates/results-table.html",
                "templates/404.html",
                "templates/index.html",
            ],
        ),
        (
            "web/assets/css",
            [
                "web/assets/css/animate.css",
                "web/assets/css/bootstrap.css",
                "web/assets/css/bootstrap.min.css",
                "web/assets/css/pe-icons.css",
                "web/assets/css/plugins.css",
                "web/assets/css/style.css",
            ],
        ),
        (
            "web/assets/font-awesome/css",
            [
                "web/assets/font-awesome/css/font-awesome.css",
                "web/assets/font-awesome/css/font-awesome.min.css",
            ],
        ),
        (
            "web/assets/font-awesome/fonts",
            [
                "web/assets/font-awesome/fonts/FontAwesome.otf",
                "web/assets/font-awesome/fonts/fontawesome-webfont.eot",
                "web/assets/font-awesome/fonts/fontawesome-webfont.svg",
                "web/assets/font-awesome/fonts/fontawesome-webfont.ttf",
                "web/assets/font-awesome/fonts/fontawesome-webfont.woff",
                "web/assets/font-awesome/fonts/fontawesome-webfont.woff2",
            ],
        ),
        (
            "web/assets/font-awesome/less",
            [
                "web/assets/font-awesome/less/animated.less",
                "web/assets/font-awesome/less/bordered-pulled.less",
                "web/assets/font-awesome/less/core.less",
                "web/assets/font-awesome/less/fixed-width.less",
                "web/assets/font-awesome/less/font-awesome.less",
                "web/assets/font-awesome/less/icons.less",
                "web/assets/font-awesome/less/larger.less",
                "web/assets/font-awesome/less/list.less",
                "web/assets/font-awesome/less/mixins.less",
                "web/assets/font-awesome/less/path.less",
                "web/assets/font-awesome/less/rotated-flipped.less",
                "web/assets/font-awesome/less/screen-reader.less",
                "web/assets/font-awesome/less/spinning.less",
                "web/assets/font-awesome/less/stacked.less",
                "web/assets/font-awesome/less/variables.less",
            ],
        ),
        (
            "web/assets/font-awesome/scss",
            [
                "web/assets/font-awesome/scss/_animated.scss",
                "web/assets/font-awesome/scss/_bordered-pulled.scss",
                "web/assets/font-awesome/scss/_core.scss",
                "web/assets/font-awesome/scss/_fixed-width.scss",
                "web/assets/font-awesome/scss/font-awesome.scss",
                "web/assets/font-awesome/scss/_icons.scss",
                "web/assets/font-awesome/scss/_larger.scss",
                "web/assets/font-awesome/scss/_list.scss",
                "web/assets/font-awesome/scss/_mixins.scss",
                "web/assets/font-awesome/scss/_path.scss",
                "web/assets/font-awesome/scss/_rotated-flipped.scss",
                "web/assets/font-awesome/scss/_screen-reader.scss",
                "web/assets/font-awesome/scss/_spinning.scss",
                "web/assets/font-awesome/scss/_stacked.scss",
                "web/assets/font-awesome/scss/_variables.scss",
            ],
        ),
        (
            "web/assets/fonts",
            [
                "web/assets/fonts/glyphicons-halflings-regular.eot",
                "web/assets/fonts/glyphicons-halflings-regular.svg",
                "web/assets/fonts/glyphicons-halflings-regular.ttf",
                "web/assets/fonts/glyphicons-halflings-regular.woff",
                "web/assets/fonts/Pe-icon-7-stroke.eot",
                "web/assets/fonts/Pe-icon-7-stroke.svg",
                "web/assets/fonts/Pe-icon-7-stroke.ttf",
                "web/assets/fonts/Pe-icon-7-stroke.woff",
            ],
        ),
        (
            "web/assets/img/agency",
            [
                "web/assets/img/agency/itokawa.jpg",
                "web/assets/img/agency/moon.jpg",
                "web/assets/img/agency/perseverence.png",
            ],
        ),
        ("web/assets/img/bg", ["web/assets/img/bg/bg6.jpg"]),
        (
            "web/assets/img",
            [
                "web/assets/img/cs.png",
                "web/assets/img/drag.png",
                "web/assets/img/loading.GIF",
                "web/assets/img/logo.png",
                "web/assets/img/logo_reverse.png",
            ],
        ),
        (
            "web/assets/img/ico",
            [
                "web/assets/img/ico/apple-touch-icon-114x114.png",
                "web/assets/img/ico/apple-touch-icon-144x144.png",
                "web/assets/img/ico/apple-touch-icon-57x57.png",
                "web/assets/img/ico/apple-touch-icon-72x72.png",
                "web/assets/img/ico/favicon.ico",
            ],
        ),
        (
            "web/assets/img/logo",
            [
                "web/assets/img/logo/cnes.png",
                "web/assets/img/logo/iau.jpg",
                "web/assets/img/logo/pole.jpg",
                "web/assets/img/logo/usgs.png",
            ],
        ),
        (
            "web/assets/js",
            [
                "web/assets/js/bootstrap.js",
                "web/assets/js/bootstrap.min.js",
                "web/assets/js/init.js",
                "web/assets/js/jquery.js",
                "web/assets/js/plugins.js",
            ],
        ),
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=required,
    entry_points={
        "console_scripts": [
            about["__name_soft__"]
            + "="
            + about["__name_soft__"]
            + ".__main__:run",
        ],
    },  # Optional
)
