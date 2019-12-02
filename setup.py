from setuptools import setup

long_description = open('README.rst').read()

setup(
    name='django-honeypot',
    version="0.8.0",
    package_dir={'honeypot': 'honeypot'},
    packages=['honeypot', 'honeypot.templatetags'],
    description='Django honeypot field utilities',
    author='James Turk',
    author_email='dev@jamesturk.net',
    license='BSD License',
    url='http://github.com/jamesturk/django-honeypot/',
    long_description=long_description,
    platforms=["any"],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Environment :: Web Environment',
    ],
    include_package_data=True,
    zip_safe=False,
    install_requires=['setuptools'],
)
