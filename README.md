# Accreditations Scraper

Script for scraping the accreditations for FINKI (FCSE).

## Installation

If you have Poetry, you can use `poetry install`, otherwise, `pip install -r requirements.txt`.

## Running

`[poetry run] python -m app [-c ...] [-l ...] [-e ...]`

Arguments:

- `-c` or `--cycle`: select the cycle of the courses you want to scrape (1, 2, 3, default is 1)
- `-l` or `--limit`: select the number of courses you wish to scrape (default is 0 to scrape all)
- `-e` or `--eexport`: select the .csv file with the results to clean up (this interrupts the normal flow of the script, by only cleaning up an existing file, and not scraping)
