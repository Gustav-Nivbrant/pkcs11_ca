"""
Test our cmc
"""
import base64
import os
import unittest

import requests

from src.pkcs11_ca_service.config import ROOT_URL

from .lib import verify_pkcs11_ca_tls_cert

CMC_ENDPOINT = "/cmc01"
CMC_CONTENT_TYPE = "application/pkcs7-mime"


class TestCMC(unittest.TestCase):
    """
    Test our CMC
    """

    if "CA_URL" in os.environ:
        ca_url = os.environ["CA_URL"]
    else:
        ca_url = ROOT_URL

    def test_cmc(self) -> None:
        """
        Test CMC response
        """

        # Assumes this cert is in config.py in CMC_REQUEST_CERTS
        # """-----BEGIN CERTIFICATE-----
        # MIIBJDCByqADAgECAgRhfDUqMAoGCCqGSM49BAMCMBoxGDAWBgNVBAMMD1Rlc3Qg
        # Q01DIENsaWVudDAeFw0yMTEwMjkxNzUzNDZaFw0yNjEwMjkxNzUzNDZaMBoxGDAW
        # BgNVBAMMD1Rlc3QgQ01DIENsaWVudDBZMBMGByqGSM49AgEGCCqGSM49AwEHA0IA
        # BJuWGZFY9U8KD8RsIALCJYElSH4GgI6/nY6L5RTPGdYl5xzF2yYKRlFQBNVbB359
        # HBmaVuhuKbTkLiKsTTy0qRMwCgYIKoZIzj0EAwIDSQAwRgIhAIitbkx60TsqHZbH
        # k9ko+ojFQ3XWJ0zTaKGQcfglrTU/AiEAjJs3LuO1F6GxDjgpLVVp+u750rVCwsUJ
        # zIqw8k4ytIY=
        # -----END CERTIFICATE-----"""

        crmf_req = (
            "MIIFUwYJKoZIhvcNAQcCoIIFRDCCBUACAQMxDTALBglghkgBZQMEAgEwggLZBggrBgEFBQcMAqCCAssEggLHMIICwzCB1zCBlgIESUvmzAYIKwYBBQUHBwYx"  # pylint: disable=line-too-long
            + "gYMEgYA0HycpETeGmY81Vgs6HQPTJILKc6vRo80OjRH+yLb7z9Pq9dUnWOUhN4zs7sWN64yjDNM+kvVv9+Nm1XpQ99t3cWkjc3WzOOgoiwiGMLdZaqZipfuC"  # pylint: disable=line-too-long
            + "0tYV9bPEfbL7ggv/Oa9BiM8NTg8t1Z7O+hJkPeVM66orh8uoB75I4G59HzAYAgQ1mgbtBggrBgEFBQcHEjEGBARjcm1mMCICBFoGN74GCCsGAQUFBwcLMRAw"  # pylint: disable=line-too-long
            + "DgIEWZphMTAGAgQchku4MIIB4aGCAd0wggHZAgQchku4MIIBz6VzMHExCzAJBgNVBAYTAlNFMSYwJAYDVQQDDB1EYXRlIE5hbWUgMjAyMy0wMS0xMSAxMzoz"  # pylint: disable=line-too-long
            + "Mjo0MjETMBEGA1UEBRMKMTIzNDU2Nzg5MDEPMA0GA1UECgwGQVAgT3JnMRQwEgYDVQQLDAtBUCBPcmcgVW5pdKZZMBMGByqGSM49AgEGCCqGSM49AwEHA0IA"  # pylint: disable=line-too-long
            + "BDVAdItFB+4+w8LbzDRZZL5mkIITDpgtdr1KMtF/6hb9CwWAB0vphsPBCsuNchoFZhJLxmLzv5Q+xNEcG72rRbOpgfwwCQYDVR0TBAIwADArBgNVHSMEJDAi"  # pylint: disable=line-too-long
            + "gCBdR6OAjX7weUrlRd0L5dGJSnuctXVf5bwtkASujE4f8DApBgNVHQ4EIgQgA3rg7ywNY3HlSfV1tXd6KGAxPyKtZyQ7F4KJZHB3IFkwDgYDVR0PAQH/BAQD"  # pylint: disable=line-too-long
            + "AgOIMDMGA1UdHwQsMCowKKAmoCSGImh0dHA6Ly9sb2NhbGhvc3Q6ODA4MC9jcmwvY2EwMS5jcmwwOwYIKwYBBQUHAQEELzAtMCsGCCsGAQUFBzABhh9odHRw"  # pylint: disable=line-too-long
            + "Oi8vbG9jYWxob3N0OjgwODAvb2NzcC9jYTAxMBUGA1UdIAQOMAwwCgYIKoVwAQIBZAEwADAAoIIBKDCCASQwgcqgAwIBAgIEYXw1KjAKBggqhkjOPQQDAjAa"  # pylint: disable=line-too-long
            + "MRgwFgYDVQQDDA9UZXN0IENNQyBDbGllbnQwHhcNMjExMDI5MTc1MzQ2WhcNMjYxMDI5MTc1MzQ2WjAaMRgwFgYDVQQDDA9UZXN0IENNQyBDbGllbnQwWTAT"  # pylint: disable=line-too-long
            + "BgcqhkjOPQIBBggqhkjOPQMBBwNCAASblhmRWPVPCg/EbCACwiWBJUh+BoCOv52Oi+UUzxnWJeccxdsmCkZRUATVWwd+fRwZmlbobim05C4irE08tKkTMAoG"  # pylint: disable=line-too-long
            + "CCqGSM49BAMCA0kAMEYCIQCIrW5MetE7Kh2Wx5PZKPqIxUN11idM02ihkHH4Ja01PwIhAIybNy7jtRehsQ44KS1Vafru+dK1QsLFCcyKsPJOMrSGMYIBITCC"  # pylint: disable=line-too-long
            + "AR0CAQEwIjAaMRgwFgYDVQQDDA9UZXN0IENNQyBDbGllbnQCBGF8NSowCwYJYIZIAWUDBAIBoIGSMBcGCSqGSIb3DQEJAzEKBggrBgEFBQcMAjAcBgkqhkiG"  # pylint: disable=line-too-long
            + "9w0BCQUxDxcNMjMwMTExMTIzMjQyWjAoBgkqhkiG9w0BCTQxGzAZMAsGCWCGSAFlAwQCAaEKBggqhkjOPQQDAjAvBgkqhkiG9w0BCQQxIgQgUdqYlBQZB3tA"  # pylint: disable=line-too-long
            + "Dk+Zw0gzs1xuoJe82Z3a6jGCkc/EAmIwCgYIKoZIzj0EAwIERjBEAiA5yd/rQaBhYfmXI0gb5LSgw27ipM5hFmWcI6Y/DuR3KQIgUrjFdfQbdqfwANUlrVUO"  # pylint: disable=line-too-long
            + "iIH0xiJbSzvKc3HEF7cEImc="
        )
        decoded = base64.b64decode(crmf_req.strip())
        req = requests.post(
            self.ca_url + CMC_ENDPOINT,
            data=decoded,
            headers={"Content-Type": CMC_CONTENT_TYPE},
            timeout=10,
            verify=verify_pkcs11_ca_tls_cert(),
        )
        self.assertTrue(req.status_code == 200)

        decoded = bytes.fromhex(
            "308205a106092a864886f70d010702a08205923082058e020103310d300b06096086480165030402013082032506082b06010505070c02a0820317048203133082030f3081b53081960204144cb15906082b0601050507070631818304818053c366a54f2f15b6fe072204febaf29448f404aced769695e759cfcc5d54e064809ad887de6a62b1ef2e90da96234f90b45aec7eb2adc45acbb5be0a8c9aa8cd04f03159a4f00a67033ea597a91f951507849b469012b0152b268046eb17785817046cf6f2c4ca895cb4f20b23767bdd5f4015fe9911f1306fb9f20df8608991301a020437db9a9606082b0601050507071231080406706b637331303082024fa082024b020446abb5fe30820241308201e60201003071310b30090603550406130253453126302406035504030c1d44617465204e616d6520323032332d30312d33302032333a31383a3433311330110603550405130a31323334353637383930310f300d060355040a0c064150204f726731143012060355040b0c0b4150204f726720556e69743059301306072a8648ce3d020106082a8648ce3d03010703420004a89e922e0de4f95f50185c185d451e7f42ce9b9f3c21cd4c23c03187090462c4c5b4b1413501ea67baf405cbe6fd5235f141a7c4802d4db732aaeb653db6cb1fa08201113082010d06092a864886f70d01090e3181ff3081fc30090603551d1304023000302b0603551d230424302280205d47a3808d7ef0794ae545dd0be5d1894a7b9cb5755fe5bc2d9004ae8c4e1ff030290603551d0e042204207f4fceb6e743d5203667dd237797ca96b9655794da4a69ad1a74f50adf6cd60a300e0603551d0f0101ff04040302038830330603551d1f042c302a3028a026a0248622687474703a2f2f6c6f63616c686f73743a383038302f63726c2f636130312e63726c303b06082b06010505070101042f302d302b06082b06010505073001861f687474703a2f2f6c6f63616c686f73743a383038302f6f6373702f6361303130150603551d20040e300c300a06082a85700102016401300a06082a8648ce3d0403020349003046022100c87792d2ca014783e90e5a6337a4abd72968542993fb121e6f98d8465936fbbc0221008889802ee8339a5ec4993c8c3a55071a175b48457ca67d88f3fab0f996b3c35f30003000a0820128308201243081caa0030201020204617c352a300a06082a8648ce3d040302301a3118301606035504030c0f5465737420434d4320436c69656e74301e170d3231313032393137353334365a170d3236313032393137353334365a301a3118301606035504030c0f5465737420434d4320436c69656e743059301306072a8648ce3d020106082a8648ce3d030107034200049b96199158f54f0a0fc46c2002c2258125487e06808ebf9d8e8be514cf19d625e71cc5db260a46515004d55b077e7d1c199a56e86e29b4e42e22ac4d3cb4a913300a06082a8648ce3d040302034900304602210088ad6e4c7ad13b2a1d96c793d928fa88c54375d6274cd368a19071f825ad353f0221008c9b372ee3b517a1b10e38292d5569faeef9d2b542c2c509cc8ab0f24e32b486318201233082011f0201013022301a3118301606035504030c0f5465737420434d4320436c69656e740204617c352a300b0609608648016503040201a08192301706092a864886f70d010903310a06082b06010505070c02301c06092a864886f70d010905310f170d3233303133303232313834335a302806092a864886f70d010934311b3019300b0609608648016503040201a10a06082a8648ce3d040302302f06092a864886f70d01090431220420dd4a4b099ed09dfbd1c16d23876771a87c56be5c33382c0d8379a9e872c5426c300a06082a8648ce3d04030204483046022100985a27657ccfbbd045584ad65e29d9fe988a13f333fca0392c44d9c9204b0db9022100ddf7c36faab8caceaead5c72d34301e7184dcd2e9a5ad91aa798fbefeaf11bd5"  # pylint: disable=line-too-long
        )
        req = requests.post(
            self.ca_url + CMC_ENDPOINT,
            data=decoded,
            headers={"Content-Type": CMC_CONTENT_TYPE},
            timeout=10,
            verify=verify_pkcs11_ca_tls_cert(),
        )
        self.assertTrue(req.status_code == 200)

        # Change the signature which causes the signature validation to fail
        decoded = bytes.fromhex(
            "308205a106092a864886f70d010702a08205923082058e020103310d300b06096086480165030402013082032506082b06010505070c02a0820317048203133082030f3081b53081960204144cb15906082b0601050507070631818304818053c366a54f2f15b6fe072204febaf29448f404aced769695e759cfcc5d54e064809ad887de6a62b1ef2e90da96234f90b45aec7eb2adc45acbb5be0a8c9aa8cd04f03159a4f00a67033ea597a91f951507849b469012b0152b268046eb17785817046cf6f2c4ca895cb4f20b23767bdd5f4015fe9911f1306fb9f20df8608991301a020437db9a9606082b0601050507071231080406706b637331303082024fa082024b020446abb5fe30820241308201e60201003071310b30090603550406130253453126302406035504030c1d44617465204e616d6520323032332d30312d33302032333a31383a3433311330110603550405130a31323334353637383930310f300d060355040a0c064150204f726731143012060355040b0c0b4150204f726720556e69743059301306072a8648ce3d020106082a8648ce3d03010703420004a89e922e0de4f95f50185c185d451e7f42ce9b9f3c21cd4c23c03187090462c4c5b4b1413501ea67baf405cbe6fd5235f141a7c4802d4db732aaeb653db6cb1fa08201113082010d06092a864886f70d01090e3181ff3081fc30090603551d1304023000302b0603551d230424302280205d47a3808d7ef0794ae545dd0be5d1894a7b9cb5755fe5bc2d9004ae8c4e1ff030290603551d0e042204207f4fceb6e743d5203667dd237797ca96b9655794da4a69ad1a74f50adf6cd60a300e0603551d0f0101ff04040302038830330603551d1f042c302a3028a026a0248622687474703a2f2f6c6f63616c686f73743a383038302f63726c2f636130312e63726c303b06082b06010505070101042f302d302b06082b06010505073001861f687474703a2f2f6c6f63616c686f73743a383038302f6f6373702f6361303130150603551d20040e300c300a06082a85700102016401300a06082a8648ce3d0403020349003046022100c87792d2ca014783e90e5a6337a4abd72968542993fb121e6f98d8465936fbbc0221008889802ee8339a5ec4993c8c3a55071a175b48457ca67d88f3fab0f996b3c35f30003000a0820128308201243081caa0030201020204617c352a300a06082a8648ce3d040302301a3118301606035504030c0f5465737420434d4320436c69656e74301e170d3231313032393137353334365a170d3236313032393137353334365a301a3118301606035504030c0f5465737420434d4320436c69656e743059301306072a8648ce3d020106082a8648ce3d030107034200049b96199158f54f0a0fc46c2002c2258125487e06808ebf9d8e8be514cf19d625e71cc5db260a46515004d55b077e7d1c199a56e86e29b4e42e22ac4d3cb4a913300a06082a8648ce3d040302034900304602210088ad6e4c7ad13b2a1d96c793d928fa88c54375d6274cd368a19071f825ad353f0221008c9b372ee3b517a1b10e38292d5569faeef9d2b542c2c509cc8ab0f24e32b486318201233082011f0201013022301a3118301606035504030c0f5465737420434d4320436c69656e740204617c352a300b0609608648016503040201a08192301706092a864886f70d010903310a06082b06010505070c02301c06092a864886f70d010905310f170d3233303133303232313834335a302806092a864886f70d010934311b3019300b0609608648016503040201a10a06082a8648ce3d040302302f06092a864886f70d01090431220420dd4a4b099ed09dfbd1c16d23876771a87c56be5c33382c0d8379a9e872c5426c300a06082a8648ce3d04030204483046022100985a27657ccfbbd045584ad65e29d9fe988a13f333fca0392c44d9c9204b0db9022100ddf7c36faab8caceaead5c72d34301e7184dcd2e9a5ad91aa798faefeaf11bd5"  # pylint: disable=line-too-long
        )
        req = requests.post(
            self.ca_url + CMC_ENDPOINT,
            data=decoded,
            headers={"Content-Type": CMC_CONTENT_TYPE},
            timeout=10,
            verify=verify_pkcs11_ca_tls_cert(),
        )
        self.assertTrue(req.status_code == 401)
