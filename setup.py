# coding=utf-8

from setuptools import setup, find_packages

setup(
    name='scrapy_ajax_utils',
    version=0.154,
    # 简短描述
    description=(
        'ajax utils for scrapy.'
    ),
    # 指定描述文件的格式，如果不指定默认为rst格式
    long_description_content_type='text/markdown',
    # 指定描述文件
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
    # 项目环境需求
    install_requires=[
            'requests>=2.14.0'
        ]
)