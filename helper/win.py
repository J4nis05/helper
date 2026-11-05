import json
import os

import ntsecuritycon as rights
import pywintypes
import win32security as security

class Windows:
    @staticmethod
    def account_name(sid: "pywintypes.SIDType | str") -> str:
        """Convert a SID to an Account Name

        Args:
            sid (PySID | str): The SID to convert, either as a PySID or in "S-1-..." form

        Returns:
            str: The Account Name, or the SID string if it cannot be resolved
        """

        if isinstance(sid, str):
            sid = security.ConvertStringSidToSid(sid)
        if not isinstance(sid, pywintypes.SIDType):
            raise TypeError(f"[Windows.account_name()] SID must be a PySID or String, got {type(sid).__name__}")

        try:
            name, domain, _ = security.LookupAccountSid(None, sid)
            return f"{domain}\\{name}" if domain else name
        except pywintypes.error:
            return security.ConvertSidToStringSid(sid)
    
    @staticmethod
    def get_permissions(path: str | os.PathLike) -> dict:
        """Return an ACL summary, not effective user permissions.

        Allow and deny entries are listed separately. An account can appear in both
        (e.g. "read" and "deny_read"); Windows then normally lets the deny win.

        Args:
            path (str | PathLike): The path to get the permissions for

        Returns:
            dict: Sorted account lists for:
                owner
                read, write, execute                     (allowed)
                deny_read, deny_write, deny_execute      (partially denied)
                deny_other                               (denied delete, change permissions or take ownership)
                no_access                                (everything denied)
                unsupported                              (ACE types that are not evaluated, as "type <n>")
        """

        if not isinstance(path, (str, os.PathLike)):
            raise TypeError(f"[Windows.get_permissions()] Path must be a String or PathLike, got {type(path).__name__}")

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
            "deny_read": set(),
            "deny_write": set(),
            "deny_execute": set(),
            "deny_other": set(),
            "no_access": set(),
            "unsupported": set(),
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

            content_rights = (
                rights.FILE_GENERIC_READ
                | rights.FILE_GENERIC_WRITE
                | rights.FILE_GENERIC_EXECUTE
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
                    result["unsupported"].add(f"type {ace_type}")
                    continue

                mask = security.MapGenericMask(ace[1], mapping)
                name = Windows.account_name(ace[2])
                denied = ace_type == rights.ACCESS_DENIED_ACE_TYPE

                if denied and mask & rights.FILE_ALL_ACCESS == rights.FILE_ALL_ACCESS:
                    result["no_access"].add(name)
                    continue

                prefix = "deny_" if denied else ""

                # Broad categories based on content-related rights.
                if mask & rights.FILE_READ_DATA:
                    result[f"{prefix}read"].add(name)

                if mask & (
                    rights.FILE_WRITE_DATA | rights.FILE_APPEND_DATA
                ):
                    result[f"{prefix}write"].add(name)

                if mask & rights.FILE_EXECUTE:
                    result[f"{prefix}execute"].add(name)

                if denied and mask & ~content_rights:
                    result["deny_other"].add(name)

        return {
            key: sorted(value) if isinstance(value, set) else value
            for key, value in result.items()
        }