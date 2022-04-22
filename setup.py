from setuptools import setup

setup(
    name='wish_bot',
    version='0.0.1',
    author="mrtedn21",
    author_email="bezgin.sasha06@gmail.com",
    python_requires='>=3.7',
    url='',
    license='',
    description='Telegram bot that store users wishes',
    install_requires=(
        'aiohttp',
        'aiodns',
        'pika',
        'msgpack',
    ),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
