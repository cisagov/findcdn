#!/usr/bin/env python3

"""
Define public exports.
"""
__all__ = ["API_URL",
           "COMMON",
           "CDNs",
           "CDNs_rev"]

"""
For use with the Censys.io api
"""
API_URL = "https://censys.io/api/v1"
#UID = "[UID]"
#SECRET = "[YOUR SECRET HERE]"

"""
Top 14 CDNs most commonly used.
"""
COMMON = {
    'Cloudflare': 'Cloudflare - https://www.cloudflare.com',
    'Incapsula': 'Incapsula - https://www.incapsula.com/',
    'Cloudfront': 'Cloudfront - https://aws.amazon.com/cloudfront/',
    'Akamai': 'Akamai - https://akamai.com',
    'Airee': 'Airee - https://airee.international',
    'CacheFly': 'CacheFly - https://www.cachefly.com/',
    'EdgeCast': 'EdgeCast - https://verizondigitalmedia.com',
    'MaxCDN': 'MaxCDN - https://www.maxcdn.com/',
    'Beluga': 'BelugaCDN - https://belugacdn.com',
    'Limelight': 'Limelight -  https://www.limelight.com',
    'Fastly': 'Fastly - https://www.fastly.com/',
    'Myracloud': 'Myra - https://myracloud.com',
    'msecnd.ne': 'Microsoft Azure - https://azure.microsoft.com/en-us/services/cdn/',
    'Clever-cloud': 'Clever Cloud - https://www.clever-cloud.com/'
}

"""
More inclusive list of available CDNs
Format: CDNs[<cdn_domain>] = <cdn_name>
"""
CDNs = {
    ".amazonaws.com":"Amazon AWS",
    "cdn.geeksforgeeks.org":"GeeksForGeeksCDN",
    ".discordapp.com":"Discord",
    ".airee.international":"Airee",
    ".myracloud.com":"Myra",
    ".msecnd.ne":"MicrosoftAzure",
    ".clever-cloud.com":"Clever-cloud",
    ".awsdn":"AWSdns",
    ".turbobytes-cdn.com":"Turbo Bytes",
    ".akadns.net":"Akamai",
    ".anankecdn.com.br":"Ananke",
    ".belugacdn.com":"BelugaCDN",
    ".cdnify.io":"CDNify",
    ".clients.turbobytes.net": "Turbo Bytes",
    ".lambdacdn.net":"LambdaCDN",
    ".akamai.net":"Akamai",
    ".akamaized.net":"Akamai",
    ".akamaiedge.net":"Akamai",
    ".akamaihd.net":"Akamai",
    ".edgesuite.net":"Akamai",
    ".edgekey.net":"Akamai",
    ".srip.net":"Akamai",
    ".akamaitechnologies.com":"Akamai",
    ".akamaitechnologies.fr":"Akamai",
    ".tl88.net":"AkamaiChinaCDN",
    ".llnwd.net":"Limelight",
    ".lldns.net":"Limelight",
    ".netdna-cdn.com":"StackPath",
    ".netdna-ssl.com":"StackPath",
    ".netdna.com":"StackPath",
    ".gfx.ms":"Limelight",
    ".adn.":"EdgeCast",
    ".wac.":"EdgeCast",
    ".wpc.":"EdgeCast",
    ".fastly.net":"Fastly",
    ".fastlylb.net":"Fastly",
    "edgecastcdn.net":"EdgeCast",
    ".systemcdn.net":"EdgeCast",
    ".transactcdn.net":"EdgeCast",
    ".v1cdn.net":"EdgeCast",
    ".v2cdn.net":"EdgeCast",
    ".v3cdn.net":"EdgeCast",
    ".v4cdn.net":"EdgeCast",
    ".v5cdn.net":"EdgeCast",
    "hwcdn.net":"Highwinds",
    ".simplecdn.net":"SimpleCDN",
    ".instacontent.net":"MirrorImage",
    ".cap-mii.net":"MirrorImage",
    ".footprint.net":"Level3",
    ".fpbns.net":"Level3",
    ".ay1.b.yahoo.com":"Yahoo",
    ".yimg.":"Yahoo",
    ".yahooapis.com":"Yahoo",
    ".google.":"Google",
    "googlesyndication.":"Google",
    "youtube.":"Google",
    ".googleusercontent.com":"Google",
    "googlehosted.com":"Google",
    ".gstatic.com":"Google",
    ".doubleclick.net":"Google",
    ".insnw.net":"InstartLogic",
    ".inscname.net":"InstartLogic",
    ".internapcdn.net":"Internap",
    ".cloudfront.net":"Cloudfront",
    ".kxcdn.com":"KeyCDN",
    ".cotcdn.net":"CotendoCDN",
    ".cachefly.net":"Cachefly",
    "bo.lt":"BO.LT",
    ".cloudflare.net":"Cloudflare",
    ".cloudflare.com":"Cloudflare",
    ".afxcdn.net":"afxcdn.net",
    ".wscdns.com":"ChinaNetCenter",
    ".wscloudcdn.com":"ChinaNetCenter",
    ".ourwebpic.com":"ChinaNetCenter",
    ".att-dsa.net":"AT&T",
    ".vo.msecnd.net":"MicrosoftAzure",
    ".azureedge.net":"MicrosoftAzure",
    ".voxcdn.net":"VoxCDN",
    ".bluehatnetwork.com":"BlueHatNetwork",
    ".swiftcdn1.com":"SwiftCDN",
    ".swiftserve.com":"SwiftServe",
    ".cdngc.net":"CDNetworks",
    ".gccdn.net":"CDNetworks",
    ".gccdn.cn":"CDNetworks",
    ".panthercdn.com":"CDNetworks",
    ".nocookie.net":"Fastly",
    ".cdn.bitgravity.com":"Tata communications",
    ".cdn.telefonica.com":"Telefonica",
    ".gslb.taobao.com":"Taobao",
    ".gslb.tbcache.com":"Alimama",
    ".mirror-image.net":"MirrorImage",
    ".yottaa.net":"Yottaa",
    ".cubecdn.net":"cubeCDN",
    ".cdn77.net":"CDN77",
    ".cdn77.org":"CDN77",
    ".incapdns.net":"Incapsula",
    ".bitgravity.com":"BitGravity",
    ".r.worldcdn.net":"OnApp",
    ".r.worldssl.net":"OnApp",
    "tbcdn.cn":"Taobao",
    ".taobaocdn.com":"Taobao",
    ".ngenix.net":"NGENIX",
    ".pagerain.net":"PageRain",
    ".ccgslb.com":"ChinaCache",
    ".ccgslb.net":"ChinaCache",
    ".c3cache.net":"ChinaCache",
    ".chinacache.net":"ChinaCache",
    ".c3cdn.net":"ChinaCache",
    ".lxdns.com":"ChinaNetCenter",
    ".speedcdns.com":"QUANTIL/ChinaNetCenter",
    ".mwcloudcdn.com":"QUANTIL/ChinaNetCenter",
    "cdn.sfr.net":"SFR",
    ".azioncdn.net":"Azion",
    ".azioncdn.com":"Azion",
    ".azion.net":"Azion",
    ".cdncloud.net.au":"MediaCloud",
    ".rncdn1.com":"ReflectedNetworks",
    ".cdnsun.net":"CDNsun",
    ".mncdn.com":"Medianova",
    ".mncdn.net":"Medianova",
    ".mncdn.org":"Medianova",
    "cdn.jsdelivr.net":"jsDelivr",
    ".nyiftw.net":"NYIFTW",
    ".nyiftw.com":"NYIFTW",
    ".resrc.it":"ReSRC.it",
    ".zenedge.net":"Zenedge",
    ".lswcdn.net":"LeaseWebCDN",
    ".lswcdn.eu":"LeaseWebCDN",
    ".revcn.net":"RevSoftware",
    ".revdn.net":"RevSoftware",
    ".caspowa.com":"Caspowa",
    ".twimg.com":"Twitter",
    ".facebook.com":"Facebook",
    ".facebook.net":"Facebook",
    ".fbcdn.net":"Facebook",
    ".cdninstagram.com":"Facebook",
    ".rlcdn.com":"Reapleaf",
    ".wp.com":"WordPress",
    ".aads1.net":"Aryaka",
    ".aads-cn.net":"Aryaka",
    ".aads-cng.net":"Aryaka",
    ".squixa.net":"section.io",
    ".bisongrid.net":"BisonGrid",
    ".cdn.gocache.net":"GoCache",
    ".hiberniacdn.com":"HiberniaCDN",
    ".cdntel.net":"Telenor",
    ".raxcdn.com":"Rackspace",
    ".unicorncdn.net":"UnicornCDN",
    ".optimalcdn.com":"OptimalCDN",
    ".kinxcdn.com":"KINXCDN",
    ".kinxcdn.net":"KINXCDN",
    ".stackpathdns.com":"StackPath",
    ".hosting4cdn.com":"Hosting4CDN",
    ".netlify.com":"Netlify",
    ".b-cdn.net":"BunnyCDN",
    ".gtimg":"Tencent"}

"""
Swap the keys with their respective value. Used for digesting results.
"""
CDNs_rev = {v: k for k,v in CDNs.items()}
