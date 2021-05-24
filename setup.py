from setuptools import setup

long_description = open("README.rst").read()

setup(
    name="django-honeypot",
    version="1.0.0",
    package_dir={"honeypot": "honeypot"},
    packages=["honeypot", "honeypot.templatetags"],
    description="Django honeypot field utilities",
    author="James Turk",
    author_email="dev@jamesturk.net",
    license="BSD License",
    url="https://github.com/jamesturk/django-honeypot/",
    long_description=long_description,
    platforms=["any"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.0",
        "Framework :: Django :: 3.1",
        "Framework :: Django :: 3.2",
        "Environment :: Web Environment",
    ],
    include_package_data=True,
    zip_safe=False,
    install_requires=["setuptools"],
)
