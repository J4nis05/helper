from typing import Optional, Dict, Any

from helper import BaseGraphClient


class GraphConnection(BaseGraphClient):
    """Microsoft Graph API client for Entra ID and Office 365 services."""
    
    def __init__(
        self,
        tenant: str, 
        client: str, 
        secret: str,
        scope: str = "https://graph.microsoft.com/.default",
        api_version: str = "v1.0",
        **kwargs
    ):
        super().__init__(
            tenant=tenant, 
            client=client, 
            secret=secret, 
            scope=scope,
            api_url="https://graph.microsoft.com", 
            api_version=api_version, 
            **kwargs,
        )

    #region SharePoint

    """
    - Drive (library) permissions:
    - GET https://graph.microsoft.com/v1.0/drives/{drive-id}/permissions
    - Folder/file permissions:
    - GET https://graph.microsoft.com/v1.0/drives/{drive-id}/items/{item-id}/permissions
    - Enumerate drive children (iterate subtree):
    - GET https://graph.microsoft.com/v1.0/drives/{drive-id}/root/children
    - GET https://graph.microsoft.com/v1.0/drives/{drive-id}/items/{item-id}/children
    - Drive’s backing list:
    - GET https://graph.microsoft.com/v1.0/drives/{drive-id}/list
    - List item permissions via driveItem:
    - GET https://graph.microsoft.com/v1.0/sites/{site-id}/lists/{list-id}/items/{item-id}/driveItem/permissions
    - Microsoft 365 Group(s) tied to site:
    - GET https://graph.microsoft.com/v1.0/sites/{site-id}/groups
    - Group membership expansion:
    - GET https://graph.microsoft.com/v1.0/groups/{group-id}/members
    - GET https://graph.microsoft.com/v1.0/groups/{group-id}/owners
    - GET https://graph.microsoft.com/v1.0/groups/{group-id}/transitiveMembers
    - Tenant SharePoint sharing settings:
    - GET https://graph.microsoft.com/v1.0/admin/sharepoint/settings
    - File retention label (via list item fields):
    - GET https://graph.microsoft.com/v1.0/sites/{site-id}/lists/{list-id}/items/{item-id}/fields
    - Sensitivity label (beta; may change):
    - GET https://graph.microsoft.com/beta/drives/{drive-id}/items/{item-id}?select=id,name,sensitivityLabel

    SharePoint REST (for gaps like classic role assignments and unique-permissions flags)
    - Site/list role definitions:
    - GET {siteUrl}/_api/web/roledefinitions
    - Role assignments:
    - GET {siteUrl}/_api/web/roleassignments
    - Has unique permissions:
    - GET {siteUrl}/_api/web/lists(guid'{listId}')/HasUniqueRoleAssignments
    - GET {siteUrl}/_api/web/getfolderbyserverrelativeurl('{serverRelativeUrl}')/ListItemAllFields/HasUniqueRoleAssignments
    - GET {siteUrl}/_api/web/getfilebyserverrelativeurl('{serverRelativeUrl}')/ListItemAllFields/HasUniqueRoleAssignments
    - Site-specific sharing capability:
    - GET https://{tenant}-admin.sharepoint.com/_api/SPO.Tenant/GetSitePropertiesByUrl?url='{siteUrl}'
    """

    def get_sharepoint_settings(self) -> dict:
        """Get the sharepoint settings."""
        return self.get_request("/admin/sharepoint/settings")

    def get_site_by_url(self, hostname: str, site_name: str) -> dict:
        """Get a site by its hostname and site name."""
        return self.get_request(f"/sites/{hostname}:/sites/{site_name}")
    
    def get_subsite_by_url(self, site_id: str) -> dict:
        """Get a subsite by its site id."""
        return self.get_request(f"/sites/{site_id}/sites")

    def get_site_permissions(self, site_id: str) -> dict:
        """Get the permissions of a site."""
        return self.get_request(f"/sites/{site_id}/permissions")

    def get_site_root_drive(self, site_id: str) -> dict:
        """Get the root drive of a site."""
        return self.get_request(f"/sites/{site_id}/drive")
    
    def get_site_drives(self, site_id: str) -> dict:
        """Get the drives of a site."""
        return self.get_request(f"/sites/{site_id}/drives")
    
    def get_drive(self, drive_id: str) -> dict:
        """Get a drive."""
        return self.get_request(f"/drives/{drive_id}")

    def get_drive_permissions(self, drive_id: str) -> dict:
        """Get the permissions of a drive."""
        return self.get_request(f"/drives/{drive_id}/permissions")
    
    def get_drive_items(self, drive_id: str) -> dict:
        """Get the items of a drive."""
        return self.get_request(f"/drives/{drive_id}/root/children")
    
    def get_drive_item_permissions(self, drive_id: str, item_id: str) -> dict:
        """Get the permissions of a drive item."""
        return self.get_request(f"/drives/{drive_id}/items/{item_id}/permissions")
    
    def get_drive_item_children(self, drive_id: str, item_id: str) -> dict:
        """Get the children of a drive item."""
        return self.get_request(f"/drives/{drive_id}/items/{item_id}/children")
    #endregion

    #region Entra ID
    def get_organisation(self) -> dict:
        """Get the organisation."""
        return self.get_request("organization")

    def get_authorization_policy(self) -> dict:
        """Get the authorization policy."""
        return self.get_request("policies/authorizationPolicy")

    def get_activity_based_timeout_policies(self) -> dict:
        """Get the activity based timeout policies."""
        return self.get_request("policies/activityBasedTimeoutPolicies")

    def get_setting_templates(self) -> dict:
        """Get the setting templates."""
        self.api_version = "beta"
        result = self.get_request("directorySettingTemplates")
        self.api_version = "v1.0"
        return result

    def get_settings(self) -> dict:
        """Get the settings."""
        self.api_version = "beta"
        result = self.get_request("settings")
        self.api_version = "v1.0"
        return result
    
    def get_subscribed_skus(self) -> dict:
        """Get the subscribed SKUs."""
        return self.get_request("subscribedSkus")
    #endregion

    #region Identity Security & Authentication Methods
    def get_authentication_methods_policy(self) -> dict:
        """Get the authentication methods policy."""
        self.api_version = "beta"
        result = self.get_request("policies/authenticationMethodsPolicy")
        self.api_version = "v1.0"
        return result

    def get_authentication_method_configurations(self) -> dict:
        """Get authentication method configurations."""
        self.api_version = "beta"
        result = self.get_all_pages("authenticationMethodConfigurations")
        self.api_version = "v1.0"
        return result

    def get_user_authentication_methods(self, user_id: str) -> dict:
        """Get authentication methods for a specific user."""
        self.api_version = "beta"
        result = self.get_all_pages(f"users/{user_id}/authentication/methods")
        self.api_version = "v1.0"
        return result

    def get_identity_security_defaults_policy(self) -> dict:
        """Get the identity security defaults enforcement policy."""
        return self.get_request("policies/identitySecurityDefaultsEnforcementPolicy")

    def get_authentication_strength_policies(self) -> dict:
        """Get authentication strength policies."""
        self.api_version = "beta"
        result = self.get_all_pages("identity/conditionalAccess/authenticationStrength/policies")
        self.api_version = "v1.0"
        return result
    #endregion

    #region Conditional Access
    def get_conditional_access_policies(self) -> dict:
        """Get conditional access policies."""
        self.api_version = "beta"
        result = self.get_all_pages("identity/conditionalAccess/policies")
        self.api_version = "v1.0"
        return result

    def get_conditional_access_named_locations(self) -> dict:
        """Get conditional access named locations."""
        self.api_version = "beta"
        result = self.get_all_pages("identity/conditionalAccess/namedLocations")
        self.api_version = "v1.0"
        return result

    def get_conditional_access_templates(self) -> dict:
        """Get conditional access templates."""
        self.api_version = "beta"
        result = self.get_all_pages("identity/conditionalAccess/templates")
        self.api_version = "v1.0"
        return result

    def get_conditional_access_auth_context_refs(self) -> dict:
        """Get conditional access authentication context class references."""
        self.api_version = "beta"
        result = self.get_all_pages("identity/conditionalAccess/authenticationContextClassReferences")
        self.api_version = "v1.0"
        return result
    #endregion

    #region Applications and Service Principals
    def get_applications(self) -> dict:
        """Get all applications."""
        return self.get_all_pages("applications")

    def get_application(self, application_id: str) -> dict:
        """Get a specific application."""
        return self.get_request(f"applications/{application_id}")

    def get_service_principals(self) -> dict:
        """Get all service principals."""
        return self.get_all_pages("servicePrincipals")

    def get_service_principal(self, service_principal_id: str) -> dict:
        """Get a specific service principal."""
        return self.get_request(f"servicePrincipals/{service_principal_id}")

    def get_oauth2_permission_grants(self) -> dict:
        """Get OAuth2 permission grants."""
        return self.get_all_pages("oauth2PermissionGrants")

    def get_application_federated_identity_credentials(self, application_id: str) -> dict:
        """Get federated identity credentials for an application."""
        return self.get_all_pages(f"applications/{application_id}/federatedIdentityCredentials")

    def get_service_principal_app_role_assignments(self, service_principal_id: str) -> dict:
        """Get app role assignments for a service principal."""
        return self.get_all_pages(f"servicePrincipals/{service_principal_id}/appRoleAssignments")
    #endregion

    #region Enterprise Apps - Consent and Permissions
    def get_admin_consent_request_policy(self) -> dict:
        """Get the admin consent request policy."""
        return self.get_request("policies/adminConsentRequestPolicy")

    def get_permission_grants(self) -> dict:
        """Get permission grants."""
        return self.get_all_pages("identity/permissionGrants")

    def get_directory_audits_consent(self) -> dict:
        """Get directory audits filtered for consent activity."""
        params = {"$filter": "activityDisplayName eq 'Consent to application'"}
        return self.get_all_pages("auditLogs/directoryAudits", params=params)
    #endregion

    #region Custom Domains and Federation
    def get_domains(self) -> dict:
        """Get all domains."""
        return self.get_all_pages("domains")

    def get_domain(self, domain_id: str) -> dict:
        """Get a specific domain."""
        return self.get_request(f"domains/{domain_id}")

    def get_organization_federation_configuration(self, organization_id: str) -> dict:
        """Get federation configuration for an organization."""
        return self.get_request(f"organization/{organization_id}/federationConfiguration")

    def get_identity_providers(self) -> dict:
        """Get identity providers."""
        self.api_version = "beta"
        result = self.get_all_pages("identity/identityProviders")
        self.api_version = "v1.0"
        return result
    #endregion

    #region Users, Groups, Roles
    def get_groups(self) -> dict:
        """Get all groups."""
        return self.get_all_pages("groups")

    def get_group(self, group_id: str) -> dict:
        """Get a specific group."""
        return self.get_request(f"groups/{group_id}")

    def get_group_members(self, group_id: str) -> dict:
        """Get members of a specific group."""
        return self.get_all_pages(f"groups/{group_id}/members")

    def get_group_settings(self, group_id: str) -> dict:
        """Get settings for a specific group."""
        return self.get_request(f"groups/{group_id}/settings")

    def get_directory_roles(self) -> dict:
        """Get all directory roles."""
        return self.get_all_pages("directoryRoles")

    def get_role_definitions(self) -> dict:
        """Get role definitions."""
        return self.get_all_pages("roleManagement/directory/roleDefinitions")

    def get_role_assignments(self) -> dict:
        """Get role assignments."""
        return self.get_all_pages("roleManagement/directory/roleAssignments")

    def get_role_eligibility_schedules(self) -> dict:
        """Get role eligibility schedules (PIM)."""
        return self.get_all_pages("roleManagement/directory/roleEligibilitySchedules")

    def get_role_assignment_schedules(self) -> dict:
        """Get role assignment schedules (PIM)."""
        return self.get_all_pages("roleManagement/directory/roleAssignmentSchedules")
    
    def add_member_to_group(self, group_id: str, member_id: str) -> dict:
        """Add a member to a group."""
        return self.post_request(f"groups/{group_id}/members/$ref", {"@odata.id": f"https://graph.microsoft.com/v1.0/users/{member_id}"})
    
    def remove_member_from_group(self, group_id: str, member_id: str) -> dict:
        """Remove a member from a group."""
        return self.delete_request(f"groups/{group_id}/members/{member_id}/$ref")
    #endregion

    #region Security Defaults and Identity Protection
    def get_identity_protection_risk_detections(self) -> dict:
        """Get identity protection risk detections."""
        return self.get_all_pages("identityProtection/riskDetections")

    def get_identity_protection_risky_users(self) -> dict:
        """Get identity protection risky users."""
        return self.get_all_pages("identityProtection/riskyUsers")

    def get_identity_protection_risky_service_principals(self) -> dict:
        """Get identity protection risky service principals."""
        return self.get_all_pages("identityProtection/riskyServicePrincipals")
    #endregion

    #region Audit Logs
    def get_directory_audits(self) -> dict:
        """Get directory audit logs."""
        return self.get_all_pages("auditLogs/directoryAudits")

    def get_sign_ins(self) -> dict:
        """Get sign-in logs."""
        self.api_version = "beta"
        result = self.get_all_pages("auditLogs/signIns")
        self.api_version = "v1.0"
        return result
    #endregion

    #region Device Management
    def get_devices(self) -> dict:
        """Get all devices."""
        return self.get_all_pages("devices")

    def get_device(self, device_id: str) -> dict:
        """Get a specific device."""
        return self.get_request(f"devices/{device_id}")

    def get_primary_owner(self, device_id: str) -> dict:
        """Get the primary owner of a device."""
        return self.get_request(f"devices(deviceId='{device_id}')/registeredOwners")

    def get_managed_devices(self) -> dict:
        """Get managed devices (Intune)."""
        return self.get_all_pages("deviceManagement/managedDevices")

    def get_tenant_attach_status(self) -> dict:
        """Get tenant attach status."""
        return self.get_request("deviceManagement/tenantAttachStatus")

    def get_terms_and_conditions(self) -> dict:
        """Get terms and conditions."""
        return self.get_all_pages("deviceManagement/termsAndConditions")

    def get_compliance_policies(self) -> dict:
        """Get compliance policies."""
        return self.get_all_pages("deviceManagement/compliancePolicies")
    
    def get_bitlocker_recovery_key(self, key_id: str) -> dict:
        """Get a bitlocker recovery key."""
        return self.get_request(f"informationProtection/bitlocker/recoveryKeys/{key_id}")
    
    def get_bitlocker_recovery_keys(self) -> dict:
        """Get all bitlocker recovery keys."""
        return self.get_all_pages("informationProtection/bitlocker/recoveryKeys")
    
    def get_device_management_configurations(self) -> dict:
        """Get device management configurations."""
        return self.get_all_pages("deviceManagement/deviceConfigurations")
    
    def get_device_management_configuration(self, configuration_id: str) -> dict:
        """Get a device management configuration."""
        return self.get_request(f"deviceManagement/deviceConfigurations/{configuration_id}")
    
    def get_device_management_configuration_device_status(self, configuration_id: str) -> dict:
        """Get the device status of a device management configuration."""
        return self.get_request(f"deviceManagement/deviceConfigurations/{configuration_id}/deviceStatuses")
    #endregion

    #region Identity Governance
    def get_entitlement_management(self) -> dict:
        """Get entitlement management."""
        self.api_version = "beta"
        result = self.get_request("identityGovernance/entitlementManagement")
        self.api_version = "v1.0"
        return result

    def get_access_packages(self) -> dict:
        """Get access packages."""
        self.api_version = "beta"
        result = self.get_all_pages("identityGovernance/entitlementManagement/accessPackages")
        self.api_version = "v1.0"
        return result

    def get_entitlement_catalogs(self) -> dict:
        """Get entitlement catalogs."""
        self.api_version = "beta"
        result = self.get_all_pages("identityGovernance/entitlementManagement/catalogs")
        self.api_version = "v1.0"
        return result

    def get_access_reviews(self) -> dict:
        """Get access reviews."""
        self.api_version = "beta"
        result = self.get_all_pages("identityGovernance/accessReviews")
        self.api_version = "v1.0"
        return result

    def get_lifecycle_workflows(self) -> dict:
        """Get lifecycle workflows."""
        self.api_version = "beta"
        result = self.get_all_pages("identityGovernance/lifecycleWorkflows")
        self.api_version = "v1.0"
        return result

    def get_terms_of_use_agreements(self) -> dict:
        """Get terms of use agreements."""
        self.api_version = "beta"
        result = self.get_all_pages("identityGovernance/termsOfUse/agreements")
        self.api_version = "v1.0"
        return result
    #endregion

    #region Directory Synchronization
    def get_organization_on_premises_sync(self, organization_id: str) -> dict:
        """Get on-premises synchronization for an organization."""
        return self.get_request(f"organization/{organization_id}/onPremisesSynchronization")

    def get_directory_on_premises_sync(self) -> dict:
        """Get directory on-premises synchronization."""
        self.api_version = "beta"
        result = self.get_request("directory/onPremisesSynchronization")
        self.api_version = "v1.0"
        return result
    #endregion

    #region Teams
    def get_teams(self) -> dict:
        """Get all teams."""
        return self.get_request("teams")

    def get_team(self, team_id: str) -> dict:
        """Get a specific team."""
        return self.get_request(f"teams/{team_id}")

    def get_team_members(self, team_id: str) -> dict:
        """Get members of a team."""
        return self.get_request(f"teams/{team_id}/members")

    def get_channels(self, team_id: str) -> dict:
        """Get channels in a team."""
        return self.get_request(f"teams/{team_id}/channels")

    def get_channel(self, team_id: str, channel_id: str) -> dict:
        """Get a specific channel."""
        return self.get_request(f"teams/{team_id}/channels/{channel_id}")

    def get_channel_members(self, team_id: str, channel_id: str) -> dict:
        """Get members of a channel."""
        return self.get_request(f"teams/{team_id}/channels/{channel_id}/members")

    def get_all_channel_members(self, team_id: str, channel_id: str) -> dict:
        """Get all members of a channel (requires additional permissions)."""
        return self.get_request(f"teams/{team_id}/channels/{channel_id}/allMembers")

    def get_user_teams(self, user_id: str) -> dict:
        """Get All Associated Teams for a current user."""
        return self.get_request(f"users/{user_id}/teamwork/associatedTeams")

    def add_user_to_teams(self, user: str, team: str, channels: list, admin_channels: list, is_admin: bool = False) -> dict:
        # TODO:
        # * Validate User
        # * Validate Team ID
        # * Validate Channel IDs
        # * --> Add Handling for Name vs ID of users, teams and channels maybe

        # STEP 0 - Basic shit
        result_dict = {"value": []}
        team_endpoint = f"/teams/{team}/members"
        channels_endpoint = f"/teams/{team}/channels"

        def make_member_body(owner: bool = False) -> dict:
            body = {
                "@odata.type": "#microsoft.graph.aadUserConversationMember",
                "roles": [],
                "user@odata.bind": f"https://graph.microsoft.com/v1.0/users('{user}')",
            }
            if owner:
                body["roles"] = ["owner"]
            return body

        # STEP 1 - Add User to Team
        team_body = make_member_body(owner=is_admin)
        team_add_response = self.post_request(team_endpoint, team_body)
        if len(team_add_response.get("id", "")) > 2:
            result_dict["value"].append(
                {"type": "team", "id": team, "status": "Succeeded"}
            )
        else:
            result_dict["value"].append(
                {"type": "team", "id": team, "status": team_add_response}
            )

        # STEP 2 - Get channels and classify
        team_channels = self.get_channels(team)["value"]
        archived_channels = []
        private_channels = []
        for channel in team_channels:
            if channel.get("isArchived"):
                archived_channels.append(channel["id"])
                continue
            if channel.get("membershipType") == "private":
                private_channels.append(channel["id"])

        # STEP 3 - Add user to private channels (member)
        for channel_id in channels:
            if channel_id in archived_channels:
                result_dict["value"].append(
                    {"type": "channel", "id": channel_id, "status": "Failed >> Archived"}
                )
                continue
            if channel_id not in private_channels:
                result_dict["value"].append(
                    {"type": "channel", "id": channel_id, "status": "Failed >> Not Private"}
                )
                continue
            url = f"{channels_endpoint}/{channel_id}/members"
            channel_add_response = self.post_request(url, make_member_body(owner=False))
            if len(channel_add_response.get("id", "")) > 2:
                result_dict["value"].append(
                    {"type": "channel", "id": channel_id, "status": "Succeeded"}
                )
            else:
                result_dict["value"].append(
                    {"type": "channel", "id": channel_id, "status": channel_add_response}
                )

        # STEP 4 - Add user to private channels (owner)
        for channel_id in admin_channels:
            if channel_id in archived_channels:
                result_dict["value"].append(
                    {"type": "channel", "id": channel_id, "status": "Failed >> Archived"}
                )
                continue
            if channel_id not in private_channels:
                result_dict["value"].append(
                    {"type": "channel", "id": channel_id, "status": "Failed >> Not Private"}
                )
                continue
            url = f"{channels_endpoint}/{channel_id}/members"
            channel_add_response = self.post_request(url, make_member_body(owner=True))
            if len(channel_add_response.get("id", "")) > 2:
                result_dict["value"].append(
                    {"type": "channel", "id": channel_id, "status": "Succeeded"}
                )
            else:
                result_dict["value"].append(
                    {"type": "channel", "id": channel_id, "status": channel_add_response}
                )

        return result_dict
    #endregion

    #region Users
    def get_users(self) -> dict:
        """Get all users."""
        return self.get_all_pages("users")

    def get_user(self, user_id: str) -> dict:
        """Get a specific user."""
        return self.get_request(f"users/{user_id}")

    def get_user_settings(self, user_id: str) -> dict:
        """Get user settings."""
        return self.get_request(f"users/{user_id}/settings")

    def get_user_manager(self, user_id: str) -> dict:
        """Get user's manager."""
        return self.get_request(f"users/{user_id}/manager")

    def set_user_manager(self, user_id: str, manager_id: str) -> dict:
        """Set user's manager."""
        return self.patch_request(f"users/{user_id}/manager/$ref", {"@odata.id": f"https://graph.microsoft.com/v1.0/users/{manager_id}"})

    def delete_user_manager(self, user_id: str) -> dict:
        """Remove user's manager."""
        return self.delete_request(f"users/{user_id}/manager/$ref")
    
    def get_user_authentication_methods(self, user_id: str) -> dict:
        """Get user's authentication methods."""
        return self.get_request(f"users/{user_id}/authentication/methods")
    
    def delete_user_ms_authenticator_app(self, user_id: str, authmethod_id: str) -> dict:
        """Delete user's Microsoft Authenticator app."""
        return self.delete_request(f"users/{user_id}/authentication/methods/microsoftAuthenticator/{authmethod_id}")
    
    def get_owned_objects(self, user_id: str) -> dict:
        """Get objects owned by a user."""
        return self.get_request(f"users/{user_id}/ownedObjects")
    
    def get_owned_devices(self, user_id: str) -> dict:
        """Get devices owned by a user."""
        return self.get_request(f"users/{user_id}/ownedDevices")
    #endregion

    #region Helper Functions
    def get_all_pages(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Aggregate all pages from paginated Graph API responses."""
        result = {"value": []}
        page = self.get_request(endpoint, params=params)
        while page:
            vals = page.get("value")
            if isinstance(vals, list):
                result["value"].extend(vals)
            next_link = page.get("@odata.nextLink")
            if not next_link:
                break
            page = self._request("GET", next_link.replace(f"{self.api_url}/{self.api_version}/", ""))
        return result
    #endregion