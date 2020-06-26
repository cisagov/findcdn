# findCDN

[![GitHub Build Status](https://github.com/Pascal-0x90/findCDN/workflows/build/badge.svg)](https://github.com/Pascal-0x90/findCDN/actions)
[![Coverage Status](https://coveralls.io/repos/github/Pascal-0x90/findCDN/badge.svg?branch=develop)](https://coveralls.io/github/Pascal-0x90/findCDN?branch=develop)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/Pascal-0x90/findCDN.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/Pascal-0x90/findCDN/alerts/)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/Pascal-0x90/findCDN.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/Pascal-0x90/findCDN/context:python)
[![Known Vulnerabilities](https://snyk.io/test/github/Pascal-0x90/findCDN/develop/badge.svg)](https://snyk.io/test/github/Pascal-0x90/findCDN)

`findCDN`, is a tool which can scan and detect what kind of Content Distribution
Network (CDN) a domain is using. `findCDN` can save results to a file or just
output to stdout.

`findCDN` helps users of the tool accurately determine what CDN a domain is
using. The list of supported domains is listed in the
[cdn_config.py](https://github.com/Pascal-0x90/findCDN/blob/develop/src/findCDN/cdnEngine/detectCDN/cdn_config.py)
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

`findCDN` requires **Python 3.7+**. Python 2 is not supported. </br> `findCDN`
can be installed as a module using `pip` and the `requirements.txt` file in the
repository.

### Installed as a module

`findCDN` can be installed via pip:

```bash
pip install -r requirements.txt
```

It can then be run directly:

```bash
findCDN list github.com
```

**Note:** It is recommended to use a python virtual environment to install
modules and keep your environment clean. If you wish to do so, you will need
[pyenv](https://github.com/pyenv/pyenv) and the
[pyenv-virtualenv plugin](https://github.com/pyenv/pyenv-virtualenv) prior to
installing the module.

### Standalone Usage and examples

```bash
findCDN file <fileIn> [-o FILE] [-v] [-d] [--all] [--threads=<thread_count>]
findCDN list  <domain>... [-o FILE] [-v] [-d] [--all] [--threads=<thread_count>]
findCDN (-h | --help)

findCDN file domains.txt -o output_frontable.txt -t 17 -d
findCDN list dhs.gov cisa.gov -o output_frontable.txt -v
findCDN list cisa.gov
```

#### Options

```plaintext
  -h --help              Show this message.
  --version              Show the current version.
  -o FILE --output=FILE  If specified, then the JSON output file will be
                         set to the specified value.
  -v --verbose           Includes additional print statments.
  --all                  Includes domains with and without a CDN
                         in output.
  -d --double            Run the checks twice to increase accuracy.
  -t --threads=<thread_count>  Number of threads, otherwise use default.
```

#### Sample Output

```bash
user2@ubuntu:~$ findCDN list asu.edu -t 7 --double
Using 7 threads.
[Pending: 0 jobs]==[Threads: 2]: 100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 2/2 [00:00<00:00,  2.22it/s]
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

[![asciicast](https://raw.githubusercontent.com/Pascal-0x90/findCDN/develop/findCDN.gif)](https://raw.githubusercontent.com/Pascal-0x90/findCDN/develop/findCDN.gif)

### Library Usage

Since this library can be installed as a module, the findCDN program can be
called from and implemented in your own project allowing you to take advantage
of the CDN detection power of findCDN. Simply import into your project and pass
your list of domains you wish to analyze. In return, you will receive a json of
only domains with a CDN or all domains depending on the option you choose. The
status bar and output file options are also allowed too if you wish to utilize
those utilities in the tool.

The format is as follows:

```python
findCDN.main(
    domain_list: list,
    output_path: str = None,
    verbose: bool = False,
    all_domains: bool = False,
    pbar: bool = False,
    double_in: bool = False,
    threads: int = None)
```

#### Example

```python
import findCDN
import json
import sys

domains = ['google.com', 'cisa.gov', 'censys.io', 'yahoo.com', 'pbs.org', 'github.com']
resp_json, cnt = findCDN.main(domains, output_path="../output", double_in=True, threads=23)

dumped_json = json.loads(resp_json)

for domain in dumped_json['domains']:
  print(f"{domain} has CDNs:\n {dumped_json['domains'][domain]['cdns']}")
```

## How Does it Work

`findCDN` is broken into three sections:

- findCDN's main runner file.
  - Validates and organizes inputted domains.
  - Orchestrates the use of the Fronting Engine with set of domains.
  - Output frontable domains in JSON to stdout and to a file if seleted.
- The Fronting Engine.
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
