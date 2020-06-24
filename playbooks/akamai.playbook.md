# Domain Fronting For Akamai

**Author:** Pascal-0x90

**Working As of Date (WAD):** N/A

**CDN Organization:** Akamai Technologies

**Potential CDN Endpoints:**

## Conditions To meet

In order to front the given domain, the following conditions must be met for
success:

- Target must be on Akamai Technologies CDN
- Owned asset or fronted domain must be on Akamai CDN

## Execution Steps

1. Currently, we do not have a technique in place to front Akamai domains. Upon
   fronting the domain with normal fronting techniques, we get the following
   message:

   ```plaintext
   Access Denied
   You don't have permission to access "/L/16382/44707/1m/www.telegraph.co.uk/" on this server.

   Reference #18.961fc917.1593022866.609b08db
   ```

   This was when using the following command:

   ```bash
   curl https://www.telegraph.co.uk -H "Host: www.cricket.com.au"
   ```

2. At this time, we do not have any leads on whether Akamai Technologies is
   using ESNI which could potentially allow for a similar attack as mentioned in
   the cloudflare playbook.

## Potential Issues and Errors

- Currently does not work.
