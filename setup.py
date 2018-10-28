from setuptools import setup


from setuptools import setup

setup(
    name='shadow',
    version='0.1',
    keywords='Easy commandline encryption',
    packages=['shadow'],
    install_requires=[
        'tar-progress',
        'click',
        'tqdm'
        ],
    entry_points='''
        [console_scripts]
        shadow=shadow.cli:main
    '''
)
