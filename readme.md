<img src="images/jobfunnel_banner.png" alt="JobFunnel Banner" /> <br /> <br />
[![Build Status](https://travis-ci.com/PaulMcInnis/JobFunnel.svg?branch=master)](https://travis-ci.com/PaulMcInnis/JobFunnel)
[![Code Coverage](https://codecov.io/gh/PaulMcInnis/JobFunnel/branch/master/graph/badge.svg)](https://codecov.io/gh/PaulMcInnis/JobFunnel)

Automated tool for scraping job postings into a `.csv` file.

### Benefits over job search sites:

* Never see the same job twice!
* Browse all search results at once, in an easy to read/sort spreadsheet.
* Keep track of all explicitly new job postings in your area.
* See jobs from multiple job search sites all in one place.
* Now with the easy_apply extension, you can manipulate the csv and browse your jobs directly from the terminal.

The spreadsheet for managing your job search:

![masterlist.csv][masterlist]

### Dependencies

JobFunnel requires [Python][python] 3.6 or later. <br />
All dependencies are listed in `setup.py`, and can be installed automatically with `pip` when installing JobFunnel.

### Installing JobFunnel

```
pip install git+https://github.com/thebigG/JobFunnel.git
funnel --help
```

If you want to develop JobFunnel, you may want to install it in-place:

```
git clone https://github.com/thebigG/JobFunnel.git jobfunnel
pip install -e ./jobfunnel
funnel --help
```

### Using JobFunnel

1. Set your job search preferences in the `yaml` configuration file (or use `-kw`).
1. Run `funnel` to scrape all-available job listings.
1. Review jobs in the master-list, update the job `status` to other values such as `interview` or `offer`.
1. Set any undesired job `status` to `archive`, these jobs will be removed from the `.csv` next time you run `funnel`.
1. Check out [demo/readme.md][demo] if you want to try the demo.

__*Note*__: `rejected` jobs will be filtered out and will disappear from the output `.csv`.

### Usage Notes

* **Custom Status** <br/>
  Note that any custom states (i.e `applied`) are preserved in the spreadsheet.

* **Running Filters** <br />
  To update active filters and to see any `new` jobs going forwards, just run `funnel` again, and review the `.csv` file.

* **Recovering Lost Master-list** <br />
  If ever your master-list gets deleted you still have the historic pickle files. <br />
  Simply run `funnel --recover` to generate a new master-list.

* **Managing Multiple Searches** <br />
  You can keep multiple search results across multiple `.csv` files:
  ```
  funnel -kw Python -o python_search
  funnel -kw AI Machine Learning -o ML_search
  ```

* **Filtering Undesired Companies** <br />
Filter undesired companies by providing your own `yaml` configuration and adding them to the black list(see `JobFunnel/jobfunnel/config/settings.yaml`).
  
* **Filtering Old Jobs**<br />
  Filter jobs that you think are too old:
  `funnel -s JobFunnel/demo/settings.yaml --max_listing_days 30` will filter out job listings that are older than 30 days.


* **Automating Searches** <br />
  JobFunnel can be easily automated to run nightly with [crontab][cron] <br />
  For more information see the [crontab document][cron_doc].
  
  **NOTE ABOUT AUTOMATING:** As of right now, Glassdoor requires a human to complete a CAPTCHA. Therefore, in the case of automating with something like cron, you need to be **physically present** to complete the Glassdoor CAPTCHA. 
  
  You may also of course disable the Glassdoor scraper in your `settings.yaml` to not have to complete any CAPTCHA at all:
``` 
#- 'GlassDoor' 
- 'Indeed'
- 'Monster'
```

* **Reviewing Jobs in Terminal** <br />
  You can review the job list in the command line:
  ```
  column -s, -t < master_list.csv | less -#2 -N -S
  ```
* **Saving Duplicates** <br />
  You can save removed duplicates in a separate file, which is stored in the same place as your master list: <br />
  ```
  funnel --save_dup
  ```
* **Respectful Delaying** <br />
  Respectfully scrape your job posts with our built-in delaying algorithm, which can be configured using a config file (see `JobFunnel/jobfunnel/config/settings.yaml`) or with command line arguments:
  - `-d` lets you set your max delay value: `funnel -s demo/settings.yaml -kw AI -d 15`
  - `-r` lets you specify if you want to use random delaying, and uses `-d` to control the range of randoms we pull from: <br /> `funnel -s demo/settings.yaml -kw AI -r`
  - `-c` specifies converging random delay, which is an alternative mode of random delay. Random delay needed to be turned on as well for it to work. Proper usage would look something like this: <br /> `funnel -s demo/settings.yaml -kw AI -r -c`
  - `-md` lets you set a minimum delay value: <br /> `funnel -s demo/settings.yaml -d 15 -md 5`
  - `--fun` can be used to set which mathematical function (`constant`,  `linear`, or `sigmoid`) is used to calculate delay: <br /> `funnel -s demo/settings.yaml --fun sigmoid`
  - `--no_delay` Turns off delaying, but it's usage is not recommended.

  To better understand how to configure delaying, check out [this Jupyter Notebook][delay_jp] breaking down the algorithm step by step with code and visualizations.

<!-- links -->
[masterlist]:demo/assests/demo.png "masterlist.csv"
[python]:https://www.python.org/
[demo]:demo/readme.md
[cron]:https://en.wikipedia.org/wiki/Cron
[cron_doc]:docs/crontab/readme.md
[conc_fut]:https://docs.python.org/dev/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor
[thread]: https://docs.python.org/3.8/library/threading.html
[delay_jp]:https://github.com/bunsenmurder/Notebooks/blob/master/jobFunnel/delay_algorithm.ipynb

### easy_apply extension

The easy_apply extension nicely integrates with JobFunnel to make your job search even easier!

It will open as many browser tabs as you tell it to with randomly or per date(oldest/newest) selected job links. It also marks those same jobs with a custom status of your choosing(the default is "archive").

Once you have your scraped "master_list.csv" file, you can start using easy_apply.

If you ran JobFunnel like this:

	funnel -s settings.yaml


Make sure you stay in the same directory and then all you have to do is this:

	funnel -s settings.yaml easy_apply --ea_number 2



Two browser tabs should open up for your job applications.
These two jobs will be marked as "archive" in the csv master_list.

However, if you passed your own output path like this:

	
~~funnel -s settings.yaml -o PATH~~


I don't recommend passhing your own output PATH. It will make things confusing. It confused the heck out of me for sure. If you want  your own output path, create a new directory and copy your `settings.yaml` to that new directory. cd into that diretory and run funnel easy_apply there just like above.

**Remeber that JobFunnel considers ALL paths relative to the settings.yaml file. So I recommend to ALWAYS pass the settings.yaml path.**




You can also set a specific status for the jobs you are applying for

	funnel  -s settings.yaml easy_apply --ea_number 2 --ea_status offer


Two browser tabs should open up for your job applications.
These two jobs will be marked as "offer" in the csv master_list.

Or you could do no arguments:

	funnel  -s settings.yaml easy_apply

One browser tab should open up for your job application.
This job will be marked as "archive" in the csv master_list.

You can also tell easy_apply whether you want the oldest or newest jobs from the master_list.

	funnel -s settings.yaml easy_apply --ea_number 15 --ea_mode newest

This will open 15 job posintgs(as tabs) on your browser that have the newest date(most recent) on their row.

Of course you may also just apply to the oldest jobs as well

	funnel -s settings.yaml easy_apply --ea_number 15 --ea_mode oldest 

Likewise, the command above wil open 15 browser tabs with the oldest job postings from the master_list.

You can ask for help on all options for easy_apply from the command line:

	funnel easy_apply --h
