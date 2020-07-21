# Project to get politician speech

## Contains

* Jupyter notebook to scrap Emmanuelle Macron "discours"
* Python script

## Requirements

* python3
* python libraries
    * requests
    * pandas
    * beautifulsoup (`pip install beautifulsoup4`)


## How to use

#### linux
* Install python3 (`apt install python3`)
* Ensure pip is installed: `pip --version`
    if not, run `python -m ensurepip --default-pip`
    or 
    ```
    wget https://bootstrap.pypa.io/get-pip.py
    python3 get-pip.py --prefix=/usr/local/
    ```
* Upgrade: `python -m pip install --upgrade pip setuptools wheel`
* `pip install "required library"` example `pip install pandas`

#### windows
* Install python3
* Install the required library
* Run discours-macron.py