# Installation
Installation of `text_sensitivity` requires `Python 3.8` or higher.

### 1. Python installation
Install Python on your operating system using the [Python Setup and Usage](https://docs.python.org/3/using/index.html) guide.

### 2. Installing `text_sensitivity`
`text_sensitivity` can be installed:

* _using_ `pip`: `pip3 install` (released on [PyPI](https://pypi.org/project/text-sensitivity/))
* _locally_: cloning the repository and using `python3 setup.py install`

#### Using `pip`
1. Open up a `terminal` (Linux / macOS) or `cmd.exe`/`powershell.exe` (Windows)
2. Run the command:
    - `pip3 install text_sensitivity`, or
    - `pip install text_sensitivity`.

```console
user@terminal:~$ pip3 install text_sensitivity
Collecting text_sensitivity
...
Installing collected packages: text-sensitivity
Successfully installed text-sensitivity
```

#### Locally
1. Download the folder from `GitLab/GitHub`:
    - Clone this repository, or 
    - Download it as a `.zip` file and extract it.
2. Open up a `terminal` (Linux / macOS) or `cmd.exe`/`powershell.exe` (Windows) and navigate to the folder you downloaded `text_sensitivity` in.
3. In the main folder (containing the `setup.py` file) run:
    - `python3 setup.py install`, or
    - `python setup.py install`.

```console
user@terminal:~$ cd ~/text_sensitivity
user@terminal:~/text_explanability$ python3 setup.py install
running install
running bdist_egg
running egg_info
...
Finished processing dependencies for text-sensitivity
```
