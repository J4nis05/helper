import json
import os

import ntsecuritycon as rights
import pywintypes
import win32security as security

class Windows:
    @staticmethod
    def account_name(sid: str) -> str:
        """Convert a SID to an Account Name

        Args:
            sid (str): The SID to convert

        Returns:
            str: The Account Name
        """

        assert type(sid) == str, "[Windows.account_name()] SID must be a string"
        
        try:
            name, domain, _ = security.LookupAccountSid(None, sid)
            return f"{domain}\\{name}" if domain else name
        except pywintypes.error:
            return security.ConvertSidToStringSid(sid)
    
    @staticmethod
    def get_permissions(path: str) -> dict:
        """Return an ACL summary, not effective user permissions.

        Args:
            path (str): The path to get the permissions for

        Returns:
            dict: The permissions
        """

        assert type(path) == str, "[Windows.get_permissions()] Path must be a string"

        descriptor = security.GetNamedSecurityInfo(
            os.fspath(path),
            security.SE_FILE_OBJECT,
            security.OWNER_SECURITY_INFORMATION | 
            security.DACL_SECURITY_INFORMATION,
        )

        result = {
            "owner": [Windows.account_name(descriptor.GetSecurityDescriptorOwner())],
            "read": set(),
            "write": set(),
            "execute": set(),
            "no_access": set(),
        }

        dacl = descriptor.GetSecurityDescriptorDacl()

        if dacl is None:
            # A NULL DACL allows everyone discretionary access.
            everyone = Windows.account_name(
                security.ConvertStringSidToSid("S-1-1-0")
            )
            for field in ("read", "write", "execute"):
                result[field].add(everyone)
        else:
            mapping = (
                rights.FILE_GENERIC_READ,
                rights.FILE_GENERIC_WRITE,
                rights.FILE_GENERIC_EXECUTE,
                rights.FILE_ALL_ACCESS,
            )

            for index in range(dacl.GetAceCount()):
                ace = dacl.GetAce(index)
                ace_type, flags = ace[0]

                # These entries apply only to children, not this object.
                if flags & rights.INHERIT_ONLY_ACE:
                    continue

                if ace_type not in (
                    rights.ACCESS_ALLOWED_ACE_TYPE,
                    rights.ACCESS_DENIED_ACE_TYPE,
                ):
                    raise NotImplementedError(
                        f"Unsupported ACE type: {ace_type}"
                    )

                mask = security.MapGenericMask(ace[1], mapping)
                name = Windows.account_name(ace[2])

                if ace_type == rights.ACCESS_DENIED_ACE_TYPE:
                    full = rights.FILE_ALL_ACCESS
                    if mask & full == full:
                        result["no_access"].add(name)
                    elif mask:
                        raise ValueError(
                            f"Partial deny for {name}: 0x{mask:08X}. "
                            "The requested JSON schema cannot represent it."
                        )
                    continue

                # Broad categories based on content-related rights.
                if mask & rights.FILE_READ_DATA:
                    result["read"].add(name)

                if mask & (
                    rights.FILE_WRITE_DATA | rights.FILE_APPEND_DATA
                ):
                    result["write"].add(name)

                if mask & rights.FILE_EXECUTE:
                    result["execute"].add(name)

        return {
            key: sorted(value) if isinstance(value, set) else value
            for key, value in result.items()
        }