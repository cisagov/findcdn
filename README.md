# findcdn

[![GitHub Build Status](https://github.com/Pascal-0x90/findcdn/workflows/build/badge.svg)](https://github.com/Pascal-0x90/findcdn/actions)
[![Coverage Status](https://coveralls.io/repos/github/Pascal-0x90/findcdn/badge.svg?branch=develop)](https://coveralls.io/github/Pascal-0x90/findcdn?branch=develop)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/Pascal-0x90/findcdn.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/Pascal-0x90/findcdn/alerts/)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/Pascal-0x90/findcdn.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/Pascal-0x90/findcdn/context:python)
[![Known Vulnerabilities](https://snyk.io/test/github/Pascal-0x90/findcdn/develop/badge.svg)](https://snyk.io/test/github/Pascal-0x90/findcdn)

`findcdn`, is a tool which can scan and detect what kind of Content Distribution
Network (CDN) a domain is using. `findcdn` can save results to a file or just
output to stdout.

`findcdn` helps users of the tool accurately determine what CDN a domain is
using. The list of supported domains is listed in the
[cdn_config.py](https://github.com/Pascal-0x90/findcdn/blob/develop/src/findcdn/cdnEngine/detectCDN/cdn_config.py)
file in the repository. The library can be implemented as a standalone tool or a
importable module you can use in your project. In both cases you can define an
output file which the results can be written to. </br>

The original purpose of this tool was to automatically detect Domain
Frontability of a domain which uses a CDN. Due to the amount of overhead for
detection, we moved the development of the tool into a CDN detection only tool.
We use our wiki to further describe what Domain Fronting is, our research notes,
design decisions, and playbooks for fronting specific domains. If any one has
access to a CDN which we have failed to front or have no playbook for yet, feel
free to make a new playbook using the template playbook and make a pull request
to the repository.

## Project Change Summary

- Project now is for CDN detection
  - A result of not being able to support domain fronting detection for every
    CDN.
- Resources, Notes, and playbooks are available in the Wiki for the repository.
- Any feed-back, improvements, or additional playbooks are always appreciated.

## Getting Started

`findcdn` requires **Python 3.7+**. Python 2 is not supported. </br> `findcdn`
can be installed as a module using `pip` and the `requirements.txt` file in the
repository.

### Installed as a module

`findcdn` can be installed via pip:

```bash
pip install -r requirements.txt
```

It can then be run directly:

```bash
findcdn list github.com
```

**Note:** It is recommended to use a python virtual environment to install
modules and keep your environment clean. If you wish to do so, you will need
[pyenv](https://github.com/pyenv/pyenv) and the
[pyenv-virtualenv plugin](https://github.com/pyenv/pyenv-virtualenv) prior to
installing the module.

### Standalone Usage and examples

```bash
findcdn file <fileIn> [options]
findcdn list  <domain>... [options]
findcdn (-h | --help)

findcnd -h
findcdn file domains.txt -o output_cdn.txt -t 17 -d
findcdn list dhs.gov cisa.gov -o output_cnd.txt -v
findcdn list cisa.gov
```

#### Options

```plaintext
  -h --help                    Show this message.
  --version                    Show the current version.
  -o FILE --output=FILE        If specified, then the JSON output file will be
                               created at the specified value.
  -v --verbose                 Includes additional print statements.
  --all                        Includes domains with and without a CDN
                               in output.
  -d --double                  Run the checks twice to increase accuracy.
  -t --threads=<thread_count>  Number of threads, otherwise use default.
  --timeout=<timeout>          Max duration in seconds to wait for a domain to
                               conclude processing, otherwise use default.
  --user_agent=<user_agent>    Set the user agent to use, otherwise
                               use default.
```

#### Sample Output

```bash
user2@ubuntu:~$ findcdn list asu.edu -t 7 --double
Using 7 threads.
[Pending: 0 jobs]==[Threads: 2]: 100%|███████████████████████████████| 2/2 [00:00<00:00,  2.22it/s]
{
    "date": "06/19/2020, 13:00:38",
    "CDN_count": "1",
    "domains": {
        "asu.edu": {
            "IP": "'104.16.50.14'",
            "cdns": "'.cloudflare.com'",
            "cdns_by_names": "'Cloudflare'"
        }
    }
}
Domain processing completed.
1 domains had CDN's out of 1.

```

[![asciicast](https://raw.githubusercontent.com/Pascal-0x90/findcdn/develop/findcdn.gif)](https://raw.githubusercontent.com/Pascal-0x90/findcdn/develop/findcdn.gif)

### Library Usage

Since this library can be installed as a module, the findcdn program can be
called from and implemented in your own project allowing you to take advantage
of the CDN detection power of findcdn. Simply import into your project and pass
your list of domains you wish to analyze. In return, you will receive a json of
only domains with a CDN or all domains depending on the option you choose. The
status bar and output file options are also allowed too if you wish to utilize
those utilities in the tool.

The format is as follows:

```python
findcdn.main(
    domain_list: List[str],  # List of domains to search
    output_path: str = None,  # if included, output results to json
    verbose: bool = False,  # Verbose mode (more printing!)
    all_domains: bool = False,  # Includes domains that dont have cdn's in the output
    interactive: bool = False,  # Includes a progress bar (normally used for command line)
    double_in: bool = False,  #D ouble the number of tries on a domain to increase accuracy
    threads: int = THREADS,  # Number of threads to use
    timeout: int = TIMEOUT,  # How long to wait on a domain
    user_agent: str = USER_AGENT,  # User Agent to use
) -> str:
```

#### Example

```python
import findcdn
import json

domains = ['google.com', 'cisa.gov', 'censys.io', 'yahoo.com', 'pbs.org', 'github.com']
resp_json = findcdn.main(domains, output_path="output.json", double_in=True, threads=23)

dumped_json = json.loads(resp_json)

for domain in dumped_json['domains']:
    print(f"{domain} has CDNs:\n {dumped_json['domains'][domain]['cdns']}")
```

## How Does it Work

`findcdn` is broken into three sections:

- findcdn's main runner file.
  - Validates and organizes inputted domains.
  - Orchestrates the use of the CDN Engine with set of domains.
  - Output domain CDN's in JSON to stdout and to a file if seleted.
- The CDN Engine.
  - Organizes all domains into a "pot".
  - `Chef` will use the CDN Detection library to obtain all CDNs for each
    domain.
  - `Chef` then runs analysis to set the boolean has_cdn value if it detects a
    domain is has a CDN then returns the list of domains back to the runner
    file.
- CDN Detection.
  - Will scrape data from:
    - HTTPS Server Headers.
    - CNAME records.
    - WHOIS data.
  - From each of these, it runs a fingerprint scan to identify any CDNs defined
    in `cdn_config.py` which may be substrings inside of the data found here.

## More Information

There is more information located
[in our wiki page](https://github.com/Pascal-0x90/findcdn/wiki). Feel free to
make pull requests for anything you would like to see added into the wiki of
this repo. This can be any of the following:

- Information pertaining to domain fronting.
- Playbooks for fronting different domains.
- Better detection methods for CDN.
- General updates to current pages.

## Contributing

We welcome contributions! Please see [here](CONTRIBUTING.md) for details.

## License

This project is in the worldwide [public domain](LICENSE).

This project is in the public domain within the United States, and copyright and
related rights in the work worldwide are waived through the
[CC0 1.0 Universal public domain dedication](https://creativecommons.org/publicdomain/zero/1.0/).

All contributions to this project will be released under the CC0 dedication. By
submitting a pull request, you are agreeing to comply with this waiver of
copyright interest.
