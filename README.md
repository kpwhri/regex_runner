[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]



<!-- PROJECT LOGO -->
<br />
<div>
  <p>
    <a href="https://github.com/kpwhri/runrex">
      <img src="images/logo.png" alt="Logo">
    </a>
  </p>

  <h3 align="center">Runrex</h3>

  <p>
    Library to aid in organizing, running, and debugging regular expressions against large bodies of text.
  </p>
</div>


<!-- TABLE OF CONTENTS -->
## Table of Contents

* [About the Project](#about-the-project)
* [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
* [Usage](#usage)
* [Roadmap](#roadmap)
* [Contributing](#contributing)
* [License](#license)
* [Contact](#contact)
* [Acknowledgements](#acknowledgements)



## About the Project 
The goal of this library is to simplify the deployment of regular expression on large bodies of text, in a variety of input formats.


<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple steps.

### Prerequisites

* Python 3.8+
* runrex package: https://github.com/kpwhri/runrex

### Installation
 
1. Clone the repo
    ```sh
    git clone https://github.com/kpwhri/runrex.git
    ```
2. Install requirements (`requirements-dev` is for test packages)
    ```sh
    pip install -r requirements.txt -r requirements-dev.txt
    ```
3. If you wish to read text from SAS or SQL, you will need to install additional requirements. These additional requirements files may be of use:
    - ODBC-connection: `requirements-db.txt`
    - Postgres: `requirements-psql.txt`
    - SAS: `requirements-sas.txt`
4. Run tests.
    ```sh
    set/export PYTHONPATH=src
    pytest tests
    ```

## Usage

### Example Implementations
* [Anaphylaxis](https://github.com/kpwhri/anaphylaxis-runrex)
* [PCOS](https://github.com/kpwhri/pcos-runrex)

### Build Customized Algorithm

* Create 4 files:
    * `patterns.py`: defines regular expressions of interest
        * See `examples/example_patterns.py` for some examples
    * `test_patterns.py`: tests for those regular expressions
        * Why? Make sure the patterns do what you think they do
    * `algorithm.py`: defines algorithm (how to use regular expressions); returns a Result
        * See `examples/example_algorithm.py` for guidance
    * `config.(py|json|yaml)`: various configurations defined in `schema.py`
        * See example in `examples/example_config.py` for basic config  

## Input Data

Accepts a variety of input formats, but will need to at least specify a `document_id` and `document_text`. The names are configurable.

### Sentence Splitting

By default, the input document text is expected to have each sentence on a separate line. If a sentence splitting scheme is desired, it will need to be supplied to the application. 

### Schema/Examples
For more details, see the [example config](https://github.com/kpwhri/runrex/blob/master/examples/example_config.py) 
or consult the [schema](https://github.com/kpwhri/runrex/blob/master/src/runrex/schema.py)

## Output Format

* Recommended output format is `jsonl`
    - The data can be extracted using python:
```python
import json
with open('output.jsonl') as fh:
    for line in fh:
         data = json.loads(line)  # data is dict
```

* Output variables are configurable and can include:
    - **id**: unique id for line
    - **name**: document name
    - **algorithm**: name of algorithm with finding
    - **value**
    - **category**: name of category (usually the pattern; multiple categories contribute to an algorithm)
    - **date**
    - **extras**
    - **matches**: pattern matches
    - **text**: captured text
    - **start**: start index/offset of match
    - **end**: end index/offset of match

* Scripts to accomplish useful tasks with the output are included in the `scripts` directory.

## Versions

Uses [SEMVER](https://semver.org/).

See https://github.com/kpwhri/runrex/releases.

<!-- ROADMAP -->
## Roadmap

See the [open issues](https://github.com/kpwhri/runrex/issues) for a list of proposed features (and known issues).



<!-- CONTRIBUTING -->
## Contributing

Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


<!-- LICENSE -->
## License

Distributed under the MIT License. 

See `LICENSE` or https://kpwhri.mit-license.org for more information.



<!-- CONTACT -->
## Contact

Please use the [issue tracker](https://github.com/kpwhri/runrex/issues). 


<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/kpwhri/runrex.svg?style=flat-square
[contributors-url]: https://github.com/kpwhri/runrex/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/kpwhri/runrex.svg?style=flat-square
[forks-url]: https://github.com/kpwhri/runrex/network/members
[stars-shield]: https://img.shields.io/github/stars/kpwhri/runrex.svg?style=flat-square
[stars-url]: https://github.com/kpwhri/runrex/stargazers
[issues-shield]: https://img.shields.io/github/issues/kpwhri/runrex.svg?style=flat-square
[issues-url]: https://github.com/kpwhri/runrex/issues
[license-shield]: https://img.shields.io/github/license/kpwhri/runrex.svg?style=flat-square
[license-url]: https://kpwhri.mit-license.org/
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=flat-square&logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/company/kaiser-permanente-washington
<!-- [product-screenshot]: images/screenshot.png -->