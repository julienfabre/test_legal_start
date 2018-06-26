# Usage

If virtualenv is not installed, install it:
```sh
pip install virtualenv
```

Create a Python virtual environment:
```sh
virtualenv env
```

Activate the virtual environment:
```sh
source env/bin/activate
```

Install the requirement (pytest):
```sh
pip install -r requirements.txt
```

Run the program:
```sh
python tom_thumb_parser.py
```

Launch unit tests:
```
py.test tests.py
```
