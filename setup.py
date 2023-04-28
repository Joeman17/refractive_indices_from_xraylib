from setuptools import setup

#Following https://uoftcoders.github.io/studyGroup/lessons/python/packages/lesson/

#Look here https://stackoverflow.com/questions/458550/standard-way-to-embed-version-into-python-package
exec(open('refractive_indices_from_xraylib/version.py').read())

requires = ['xraylib']

setup(
    # Needed to silence warnings (and to be a worthwhile package)
    name='refractive_indices_from_xraylib',
    url='https://github.com/Joeman17/refractive_indices_from_xraylib',
    author='Thomas Jentschke',
    author_email='thomas.jentschke@hereon.de',
    # Needed to actually package something
    packages=['refractive_indices_from_xraylib'],
    # Needed for dependencies
    install_requires=['numpy'] + requires,
    # *strongly* suggested for sharing
    version=__version__,
    # The license can be anything you like
    license='GPL3',
    description='Extracts refractive indices from xraylib. Optionally the refractive indices can be saved into a .txt file.',
)
