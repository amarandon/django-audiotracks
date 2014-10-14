from setuptools import setup


setup(
    name='django-audiotracks',
    version='0.2.5',
    description='A pluggable Django app to publish audio tracks',
    long_description=open("README.rst").read(),
    keywords='django audio sound',
    author='Alex Marandon',
    license='MIT',
    author_email='contact@alexmarandon.com',
    url='https://github.com/amarandon/django-audiotracks',
    packages=['audiotracks'],
    test_suite='audiotracks.testing.runtests.main',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        'Framework :: Django',
    ],
    install_requires=[
        'mutagen',
        'Pillow'
        ],
    include_package_data=True,
    zip_safe=False,
)
