TiebaCrawler
============

A web crawler written in python to crawl information from posts on tieba.baidu.com.

### Recommended dependency
Platform | Version
--- | ---
| Windows | 2.7.6 |
| Linux | 2.7.3 |

### For Windows Users
* Python 2.7.6 [Downloads](http://www.python.org/download/)
* To learn how to run a python program on Windows, click [here](http://docs.python.org/2/using/windows.html).

### Default Settings (stored in config.py)
Name | Description
--- | ---
Output encoding | UTF-8
Export directory | export/
Output format | CSV
Delimiter | Vertical line

### Execution
$ python main.py [-v] [-h] url

### Help
$ python main.py -h

### Troubleshooting
main.py: error: too few arguments

> This is because the program requires one URL as input to start the crawling.

Output file is all garbage code,
for example many question marks.
Solution is
[here](http://office.microsoft.com/en-001/excel-help/import-or-export-text-txt-or-csv-files-HP010099725.aspx).

> You need to import the CSV and adjust according to the default settings.

This program only works for posts from tieba.baidu.com.
URL from other website may cause an exception.
