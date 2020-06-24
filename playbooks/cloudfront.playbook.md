# Domain Fronting For cloudfront.com

**Author:** DoctorEww

**Working As of Date (WAD):** 06/24/20

**CDN Organization:** CloudFront

**Potential CDN Endpoints:** TODO

## Conditions To meet

In order to front the given domain, the following conditions must be met for
success:

- Must be a domain using the CloudFront CDN network.
- You must own or have a resource also on Cloudflare CDN.
- Both domains must use HTTPS.
- Both the target domain and the fronted domain must be owned by the same AWS
  account.
  - As stated by CloudFront "[i]f the two AWS accounts do not match, CloudFront
    will respond with a '421 Misdirected Request' response to give the client a
    chance to connect using the correct domain."
  - More information technical information from CloudFront on the changes done
    early 2019
    [here](https://aws.amazon.com/blogs/networking-and-content-delivery/continually-enhancing-domain-security-on-amazon-cloudfront/).

## Execution Steps

**Fronted Domain:** The allowed domain you are using as a "mask".

**Target Domain:** The domain you want to access, using the Fronted domain.

1. Follow the steps to setup two resources on
   [Amazon CloudFront](https://aws.amazon.com/cloudfront/)

   1. A account can be made for free. "AWS Free Tier includes 50GB data transfer
      out, 2,000,000 HTTP and HTTPS Requests with Amazon CloudFront"

2. Construct your HTTPS request with the target domain in the `Host:` header and
   the fronted domain as the primary domain you wish to access. The following
   two methods are just two ways to do it: (Note: both domains must be on the
   same AWS account)

   1. **cURL:**

      ```bash
      curl -H "Host: <Target_domain>" https://<Fronted_domain>
      ```

   2. **Python:**

      ```python
      import urllib.request as request

      TARGET = 'target_domain'
      FRONTED = 'https://domain.to.front'
      h = {}
      h['Host'] = TARGET
      h['User-Agent'] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"
      req = request.Request(
          FRONTED,
          data=None,
          headers=h
          )
      response = request.urlopen(req, timeout=60)

      # Check if we fronted or not, if so, print data
      if response.code == 200:
          for line in response.readlines():
              print(line.decode())
      else:
          print("Failed to front.")
      ```

## Potential Issues and Errors

- Getting both domains on the same AWS account is likely the hardest part of
  fronting with CloudFront.

## Resources

- [digi.ninja](https://digi.ninja/blog/cloudfront_example.php) (Note: This was
  written before the added security)
- [AWS Security Update](https://aws.amazon.com/blogs/networking-and-content-delivery/continually-enhancing-domain-security-on-amazon-cloudfront/)
