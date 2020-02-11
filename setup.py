# coding=utf-8

from setuptools import setup, find_packages

setup(
    name='scrapy_ajax_utils',
    version=0.154,
    description=(
        'ajax utils for scrapy.'
    ),
    long_description_content_type='text/markdown',
    long_description=open('README.md').read(),
    author='financial',
    author_email='1012593988@qq.com',
    maintainer='financial',
    maintainer_email='1012593988@qq.com',
    license='BSD License',
    packages=find_packages(),
    platforms=["all"],
    url='https://github.com/financialfly/scrapy_ajax_utils',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries'
    ],
    install_requires=[
            'scrapy>=1.7.3',
            'scrapy_splash>=0.7.2',
            'selenium>=3.141.0',
        ]
)