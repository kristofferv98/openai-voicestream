from setuptools import setup, find_packages

setup(
    name='openai_voicestream',
    version='0.1.0',
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
    url='https://github.com/kristofferv98/openai-voicestream.git',
    author='Kristoffer Vatnehol',
    author_email='kristoffer.vatnehol@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
