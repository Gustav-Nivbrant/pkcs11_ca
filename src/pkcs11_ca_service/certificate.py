"""Module to handle certificates"""
from typing import Union, Dict, List
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from python_x509_pkcs11.crl import create as create_crl

from .base import DataClassObject, InputObject, db_load_data_class
from .asn1 import pem_to_sha256_fingerprint, not_before_not_after_from_cert
from .asn1 import pem_cert_to_name_dict, cert_pem_serial_number
from .crl import Crl
from .error import WrongDataType


class CertificateInput(InputObject):
    """Class to represent certificate matching from HTTP post data """

    pem: Union[str, None]
    fingerprint: Union[str, None]


class Certificate(DataClassObject):
    """Class to represent a certificate"""

    db_table_name = "certificate"
    db_fields = {
        "public_key": int,
        "pem": str,
        "csr": int,
        "issuer": int,  # pylint:disable=duplicate-code
        "authorized_by": int,
        "fingerprint": str,
        "not_before": str,  # pylint:disable=duplicate-code
        "not_after": str,
        "created": str,
    }
    db_reference_fields = {
        "public_key": "public_key(serial)",
        "csr": "csr(serial)",
        "issuer": "ca(serial)",
        "authorized_by": "public_key(serial)",
    }
    db_unique_fields = ["pem", "fingerprint"]

    def __init__(self, kwargs: Dict[str, Union[str, int]]) -> None:
        super().__init__(kwargs)
        pem = kwargs.get("pem", None)
        if not isinstance(pem, str):  # pylint:disable=duplicate-code
            raise WrongDataType("'pem', must be a 'str'")
        self.pem = pem

        self.fingerprint = pem_to_sha256_fingerprint(self.pem)
        self.not_before, self.not_after = not_before_not_after_from_cert(self.pem)

    async def revoke(self, auth_by: int) -> str:
        """Revoke the certificate.
        https://github.com/wbond/asn1crypto/blob/b5f03e6f9797c691a3b812a5bb1acade3a1f4eeb/asn1crypto/crl.py#L97

        Parameters:
        auth_by (int): The revoker public key DB id

        Returns:
        str
        """

        issuer = vars(self).get("issuer")
        if issuer is None or issuer < 1:
            raise HTTPException(status_code=400, detail="Cannot revoke a non existing cert.")

        revoke_data = await self.db.revoke_data_for_ca(issuer)
        crl_pem = await create_crl(
            revoke_data["key_label"],
            pem_cert_to_name_dict(revoke_data["ca"]),
            serial_number=cert_pem_serial_number(self.pem),
            reason=5,
            old_crl_pem=revoke_data["crl"],
        )
        crl_obj = Crl(
            {
                "pem": crl_pem,
                "authorized_by": auth_by,
                "issuer": issuer,
            }
        )
        await crl_obj.save()

        print("Revoked " + self.pem)
        return crl_pem


async def search(input_object: InputObject) -> JSONResponse:
    """Get certificates matching the input_object pattern(s).
    Returns a fastAPI json response with a list of the certificates.

    Parameters:
    input_object (InputObject): The search pattern data.

    Returns:
    fastapi.responses.JSONResponse
    """

    certificate_objs: List[Certificate] = []
    certificate_pems: List[str] = []

    db_certificate_objs = await db_load_data_class(Certificate, input_object)
    for obj in db_certificate_objs:
        if isinstance(obj, Certificate):
            certificate_objs.append(obj)

    for certificate in certificate_objs:
        certificate_pems.append(certificate.pem)

    return JSONResponse(status_code=200, content={"certificates": certificate_pems})
