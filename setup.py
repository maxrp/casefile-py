from setuptools import setup, find_packages
from casefile import __version__

with open('README.md') as f:
    readme = f.read()

setup(
    name='casefile',
    version=__version__,
    description='',
    long_description=readme,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: DFSG approved',
        'License :: OSI Approved :: GNU Affero General Public License v3 or \
                later (AGPLv3+)',
        'Topic :: Text Processing',
        'Topic :: Utilities',
    ],
    author='Max Parmer',
    author_email='maxp@trystero.is',
    url='https://github.com/maxrp/casefile-py',
    license='AGPLv3+',
    packages=find_packages(exclude=('tests', 'docs')),
    entry_points={
        'console_scripts': [
            'cf=casefile.__main__:main'
        ]
    }
)
