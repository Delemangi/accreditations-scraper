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

The script also looks for a file called `cookies.json` in the root of the project. It should contain the cookies for the session of the site. [Here](https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg) is an example Chrome extension capable of dumping all cookies used by a page. If you do end up using the given Chrome extension, keep in that mind you should also:

- Change the domain of all cookies to `iknow.ukim.mk`
- Set the `sameSite` property of all cookies to `"None"`

if you want the scraper to work.
