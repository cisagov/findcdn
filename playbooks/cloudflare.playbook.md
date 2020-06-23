# Domain Fronting For cloudflare.com

**Author:** Pascal-0x90

**Working As of Date (WAD):** 06/23/20

**CDN Organization:** Cloudflare

**Potential CDN Endpoints:** There exist many endpoints. Run `whois` on the IP
address to verify if a Cloudflare endpoint is being used.

## Conditions To meet

In order to front the given domain, the following conditions must be met for
success:

- Must be a domain using the Cloudflare CDN network.
- You will need a [specific OpenSSL](https://github.com/sftcd/openssl) version
  which allows for Encrypted Server Name Indication.
  - More information on why here:
    [digi.ninja](https://digi.ninja/blog/cloudflare_example.php)
- You must own or have a resource also on Cloudflare CDN.

## Execution Steps

1. First, compile and setup OpenSSL following the instructions in the INSTALL.md
   in the repository.

2. Setup your headers in a file called `headers` which look like the following:

   ```html
   GET / HTTP/1.1 Host:
   <target_domain> User-Agent: front/1 Accept: */*</target_domain>
   ```

   This will be the header for which the CDN will direct our traffic.

3. We then use the following set of commands to falsify the ESNI header and talk
   to the target CDN with openssl (source:
   [digi.ninja](https://digi.ninja/blog/cloudflare_example.php)):

   ```bash
   $ export LD_LIBRARY_PATH=/path/to/openssl;
   $ ESNIRR=`dig +short txt _esni.www.cloudflare.com | sed -e 's/"//g'`
   $ (cat headers; sleep 5) | /path/to/openssl/apps/openssl s_client \
   -CApath /etc/ssl/certs/ -tls1_3 -connect www.cloudflare.com:443 -esni <target_domain> \
   -esnirr $ESNIRR -esni_strict -servername www.cloudflare.com
   ```

## Potential Issues and Errors

- This can be unreliable, currently having issues running this on MacOS; success
  has past been on Ubuntu 18.04
- This specific version needs to have `make install` run on it to make sure the
  compiled libraries are in the correct place; while we still use the
  `export LD_LIBRARY_PATH` sometimes, it still is unsure where to load the
  dynamic libraries from.

## Resources

- [digi.ninja](https://digi.ninja/blog/cloudflare_example.php)
- [Medium: Cloudflare domain fronting](https://medium.com/@themiddleblue/cloudflare-domain-fronting-an-easy-way-to-reach-and-hide-a-malware-c-c-786255f0f437)
