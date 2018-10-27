from setuptools import setup


from setuptools import setup

setup(
    name='hello',
    version='0.1',
    py_modules=['hello'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        hello=hello:say_hello
    ''',
)

setup(
    name='shadow',
    version='0.1',
    keywords='Easy commandline encryption',
    packages=['shadow'],
    install_requires=[
        'tar-progress',
        'click',
        'tqdm',
        'python-gnugpg'
    ],
    entry_points='''
        [console_scripts]
        shadow=cli:main
    '''
)
