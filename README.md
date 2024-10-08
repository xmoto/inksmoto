# Inksmoto

An [Inkscape](http://www.inkscape.org/) extension for creating X-Moto levels

## Installation
See the [INSTALL](INSTALL) file

## Usage
See http://wiki.xmoto.tuxfamily.org/index.php?title=How_to_create_smooth_levels_using_Inkscape

## License
Written by Emmanuel Gorse and publish under the GPL v2.0.

## Development
### Dependencies
- Python 3.10+
- pip 23.1.0+ ([for proper installation of `pygobject-stubs`](https://github.com/pygobject/pygobject-stubs/blob/8a954eeaca7cc8b875caaf27cebc3b5a4a99d667/README.md#project-integration))

### Setup
```bash
python -m venv .venv
source .venv/bin/activate

pip install -r requirements-dev.txt
pre-commit install
```
