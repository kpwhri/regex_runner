Library to aid in organizing, running, and debugging regular expressions against large bodies of text.

# About
The goal of this library is to simplify the deployment of regular expression on large bodies of text, in a variety of input formats.

# Usage
* Create 4 files:
    * `patterns.py`: defines regular expressions
    * `test_patterns.py`: tests for those regular expressions
    *  `algorithm.py`: defines algorithm (how to use regular expressions); returns a Result
    * `config.(py|json)`: various configurations defined in `schema.py`  

# License 
MIT License, see: https://kpwhri.mit-license.org/