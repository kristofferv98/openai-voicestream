from setuptools import setup, find_packages

setup(
    name='openai_voicestream',
    version='0.1.1',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    description='A library for real-time text to speech processing using OpenAI API.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=[
        'pyaudio',
        'httpx',
    ],
    extras_require={
        'dev': [
            'pytest',
            'flake8'
        ]
    },
    author='Kristoffer Vatnehol',
    author_email='kristoffer.vatnehol@gmail.com',
    python_requires='>=3.6',
    url='https://github.com/kristofferv98/openai-voicestream.git',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
