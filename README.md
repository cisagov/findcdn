# Do You Front

[![GitHub Build Status](https://github.com/Pascal-0x90/dyFront/workflows/build/badge.svg)](https://github.com/Pascal-0x90/dyFront/actions)
[![Coverage Status](https://coveralls.io/repos/github/Pascal-0x90/dyFront/badge.svg?branch=develop)](https://coveralls.io/github/Pascal-0x90/dyFront?branch=develop)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/Pascal-0x90/dyFront.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/Pascal-0x90/dyFront/alerts/)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/Pascal-0x90/dyFront.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/Pascal-0x90/dyFront/context:python)
[![Known Vulnerabilities](https://snyk.io/test/github/Pascal-0x90/dyFront/develop/badge.svg)](https://snyk.io/test/github/Pascal-0x90/dyFront)

`dyFront`, or "Do you Front?", is a tool to scan and detect the ability to use
Domain Fronting, on a domain. `dyFront` can save results to a file or just
output to stdout.

`dyFront` was developed to help organizations discover if their hosted domains
are susceptible to Domain Fronting. Domain fronting is an attack which allows
for circumvention of domain blocks set in place by firewalls. Where a firewall
may block a user from accessing `abcd.com` which uses CDN EFG, domain `zyx.com`
which is not blocked on the given firewall and also uses EFG, a user can access
`abcd.com` by using domain fronting and making the firewall think `zyx.com` is
being accessed instead. Detecting if your domain is susceptible to this is
important for understanding potential routes for Command and Control traffic by
bad actors who may be exfiltrating information to an alternate domain through a
trusted domain you own.

## Getting Started

`dyFront` requires **Python 3.7+**. Python 2 is not supported. </br> `dyFront`
can be installed as a module using `pip` and the `requirements.txt` file in the
repository.

### Installed as a module

`dyFront` can be installed via pip:

```bash
pip install -r requirements.txt
```

It can then be run directly:

```bash
dyFront list github.com
```

**Note:** It is recommended to use a python virtual environment to install
modules and keep your environment clean. If you wish to do so, you will need
[pyenv](https://github.com/pyenv/pyenv) and the
[pyenv-virtualenv plugin](https://github.com/pyenv/pyenv-virtualenv) prior to
installing the module.

### Usage and examples

```bash
dyFront file <fileIn> [-o FILE]
dyFront list <domain>... [-o FILE]

dyFront file domains.txt -o output_frontable.txt
dyFront list dhs.gov cisa.gov -o output_frontable.txt
dyFront list cisa.gov
```

#### Options

```plaintext
  -h --help              Show this message.
  --version              Show the current version.
  -o FILE --output=FILE  If specified, then the JSON output file will be
                         set to the specified value.
```

#### Sample Output

```bash
user2@ubuntu:~$ dyFront list censys.io
1 Domains Validated
{
    "date": "06/09/2020, 08:48:40",
    "domains": {
        "censys.io": {
            "IP": "'104.26.11.245', '104.26.10.245', '172.67.68.81'",
            "Status": "Domain Frontable",
            "cdns": "'.cloudflare.com'",
            "cdns_by_names": "'Cloudflare'"
        }
    }
}
```

## How Does it Work

`dyFront` is broken into three sections:

- dyFront's main runner file.
  - Validates and organizes inputted domains.
  - Orchestrates the use of the Fronting Engine with set of domains.
  - Output frontable domains in JSON to stdout and to a file if seleted.
- The Fronting Engine.
  - Organizes all domains into a "pot".
  - `Chef` will use the CDN Detection library to obtain all CDNs for each domain.
  - `Chef` then runs analysis to set the boolean `frontable` value if it
  detects a domain is frontable and returns the list of domains back to the
  runner file.
- CDN Detection.
  - Will scrape data from:
    - HTTPS Server Headers.
    - CNAME records.
    - Nameservers Used.
    - WHOIS data.
  - From each of these, it runs a  fingerprint scan to identify any CDNs defined
  in `cdn_config.py` which may be substrings inside of the data found here.

## More In-Depth Look at Domain Fronting

There are a variate amount of uses for Domain Fronting, from bypassing
censorship to using it in command and control communications to bypass
restrictions of a firewall by making use of a domain which is trusted and
allowing communication then to the unintended website. Such examples can be seen
in how
[APT29 managed command and control](https://www.fireeye.com/blog/threat-research/2017/03/apt29_domain_frontin.html).
</br></br> The following are a listing of resources which go into more detail
about what domain fronting is, how it can be used, and common methods for
detection:

- [Domain Fronting in a nutshell](https://www.andreafortuna.org/2018/05/07/domain-fronting-in-a-nutshell/)
- [A 101 on Domain Fronting](https://digi.ninja/blog/domain_fronting.php)
- [Domain Fronting Technique T1172 - MITRE ATT&CK Framework](https://attack.mitre.org/techniques/T1172/)
- [Blocking-resistant Communication Through Domain Fronting](https://www.bamsoftware.com/papers/fronting/)
- [Domain Fronting - Wikipedia](https://en.wikipedia.org/wiki/Domain_fronting)
- [rvrsh3ll/FindFrontableDomains](https://github.com/rvrsh3ll/FindFrontableDomains)
- [Traversing the Kill-Chain - Vincent Yiu](https://gsec.hitb.org/materials/sg2018/D2%20-%20Traversing%20the%20Kill-Chain%20-%20The%20New%20Shiny%20in%202018%20-%20Vincent%20Yiu.pdf)
- [SSL Domain Fronting 101](https://medium.com/rvrsh3ll/ssl-domain-fronting-101-4348d410c56f)

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
