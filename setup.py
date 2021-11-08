from distutils.core import setup
import setuptools

setup(name='runrex',
      version='0.3.0',
      description='Library to aid in organizing, running, and debugging regular expressions against'
                  ' a large body of text.',
      url='https://github.com/kpwhri/runrex',
      author='dcronkite',
      license='MIT',
      classifiers=[  # from https://pypi.python.org/pypi?%3Aaction=list_classifiers
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Science/Research',
          'Programming Language :: Python :: 3 :: Only',
          'Topic :: Text Processing :: Linguistic',
          'License :: OSI Approved :: MIT License',
      ],
      keywords='nlp information extraction',
      entry_points={
          'console_scripts':
              [
              ]
      },
      install_requires=['jsonschema', 'sqlalchemy', 'loguru', 'syntok'],
      package_dir={'': 'src'},
      packages=setuptools.find_packages('src'),
      package_data={},
      zip_safe=False
      )
