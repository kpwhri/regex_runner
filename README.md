Library to aid in organizing, running, and debugging regular expressions against large bodies of text.

# About
The goal of this library is to simplify the deployment of regular expression on large bodies of text, in a variety of input formats.

# Usage
* Create 4 files:
    * `patterns.py`: defines regular expressions of interest
        * See `examples/example_patterns.py` for some examples
    * `test_patterns.py`: tests for those regular expressions
        * Make sure the patterns do what you think they do
    * `algorithm.py`: defines algorithm (how to use regular expressions); returns a Result
        * See `examples/example_algorithm.py` for guidance
    * `config.(py|json)`: various configurations defined in `schema.py`
        * See example in `examples/example_config.py` for basic config  

# License 
MIT License, see: https://kpwhri.mit-license.org/