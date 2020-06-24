# Domain Fronting For Incapsula incapdns.net

- **Author:** Pascal-0x90

  **Working As of Date (WAD):** N/A

  **CDN Organization:** Imperva Incapsula CDN

  **Potential CDN Endpoints:**

## Conditions To meet

In order to front the given domain, the following conditions must be met for
success:

- Target must be on Incapsula CDN
- Owned asset or fronted domain must be on Incapsula CDN

## Execution Steps

1. Currently, we do not have a technique in place to front domains on Incapsula
   CDN. Upon fronting the domain with normal fronting techniques, we get the
   following message:

```html
<html style="height:100%">
  <head>
    <meta name="ROBOTS" content="NOINDEX, NOFOLLOW" />
    <meta name="format-detection" content="telephone=no" />
    <meta name="viewport" content="initial-scale=1.0" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1" />
    <script
      type="text/javascript"
      src="/_Incapsula_Resource?SWJIYLWA=719d34d31c8e3a6e6fffd425f7e032f3"
    ></script>
  </head>
  <body style="margin:0px;height:100%">
    <iframe
      id="main-iframe"
      src="/_Incapsula_Resource?CWUDNSAI=22&xinfo=0-16116849-0%200NNN%20RT%281593027418937%20146%29%20q%280%20-1%20-1%20-1%29%20r%280%20-1%29%20B15%284%2c200%2c0%29%20U5&incident_id=480000110055256111-70731346823086784&edet=15&cinfo=04000000&rpinfo=0"
      frameborder="0"
      width="100%"
      height="100%"
      marginheight="0px"
      marginwidth="0px"
      >Request unsuccessful. Incapsula incident ID:
      480000110055256111-70731346823086784</iframe
    >
  </body>
</html>
```

This was when using the following command on domains hosted using Imperva's
Incapusla CDN:

```bash
curl https://lms.wizlearn.com/CORP/logon_new.aspx -H "Host: www.sierramist.com"
```

At this time, we do not have any leads on whether Imperva is using ESNI which
could potentially allow for a similar attack as mentioned in the cloudflare
playbook.

## Potential Issues and Errors

- Currently does not work.
