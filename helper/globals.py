from helper import FileHandler

class Globals:
    """Global Variables Used Across the Environment"""

    class colours:
        """Colours"""

        primary_light    = "#4A90E2"  # A soft blue for primary elements
        secondary_light  = "#50E3C2"  # A mint green for secondary elements
        tertiary_light   = "#F5A623"  # A warm orange for accents
        text_light       = "#333333"  # Dark gray for readable text
        background_light = "#FFFFFF"  # Pure white for the background
        foreground_light = "#F7F7F7"  # Light gray for foreground elements

        primary_dark     = "#4A90E2"  # Same blue for consistency
        secondary_dark   = "#50E3C2"  # Same mint green for consistency
        tertiary_dark    = "#F5A623"  # Same warm orange for accents
        text_dark        = "#FFFFFF"  # Pure white for readable text
        background_dark  = "#1C1C1C"  # Very dark gray for the background
        foreground_dark  = "#333333"  # Dark gray for foreground elements

        red               = "#E22C3C"
        red_orange        = "#E83726"
        orange            = "#ED6022"
        amber             = "#FA9A2C"
        yellow            = "#FFD63D"
        lime              = "#92E649"
        green             = "#45D649"
        teal              = "#22D589"
        cyan              = "#3DDBDB"
        blue              = "#3B87F0"
        indigo            = "#874FF5"
        purple            = "#BB4FF0"
        pink              = "#FF62AF"
        magenta           = "#F64680"
        coral             = "#F2525F"
        salmon            = "#F66348"
        mint              = "#68FFB4"
        sky_blue          = "#8EFFF4"
        lavender          = "#908AF6"
        lilac             = "#DF95FF"
        burgundy          = "#6E1C24"
        auburn            = "#A13220"
        olive             = "#4C652E"
        navy              = "#104B98"
        berry             = "#9F2AA7"
        black             = "#111018"
        gray              = "#53525A"
        white             = "#F2F1F8"
        brown             = "#823216"
        blonde            = "#EFC664"
        peach             = "#F1C69C"
        warm_gray         = "#625550"
        cool_gray         = "#515768"

        light_orange      = "#FF9450"
        light_amber       = "#FFBA57"
        light_yellow      = "#FFE173"
        light_lime        = "#C9FF7A"
        light_green       = "#81FF76"
        light_blue        = "#64C6FF"
        light_pink        = "#FF87BA"
        light_gray        = "#AAAAAA"
        light_brown       = "#BE5B2D"

        dark_teal         = "#1F5E47"
        dark_lavender     = "#3D3B6C"
        dark_gray         = "#242424"
        dark_brown        = "#4C2315"

        neon_red          = "#E22C3C"
        neon_red_orange   = "#E83726"
        neon_orange       = "#ED6022"
        neon_amber        = "#FA9A2C"
        neon_yellow       = "#FFD63D"
        neon_lime         = "#92E649"
        neon_green        = "#45D649"
        neon_teal         = "#22D589"
        neon_cyan         = "#3DDBDB"
        neon_blue         = "#3B87F0"
        neon_indigo       = "#874FF5"
        neon_purple       = "#BB4FF0"
        neon_pink         = "#FF62AF"
        neon_magenta      = "#F64680"
        neon_white        = "#F2F1F8"

        dark_neon_red     = "#180607"
        dark_neon_orange  = "#1F0D05"
        dark_neon_amber   = "#251507"
        dark_neon_yellow  = "#2B1C0B"
        dark_neon_lime    = "#1B220C"
        dark_neon_green   = "#091610"
        dark_neon_teal    = "#09191D"
        dark_neon_cyan    = "#0B191C"
        dark_neon_blue    = "#09101C"
        dark_neon_indigo  = "#150B24"
        dark_neon_purple  = "#1E0B26"
        dark_neon_pink    = "#210E15"
        dark_neon_magenta = "#220A13"
        dark_neon_white   = "#131315"


    class paths:
        """Commonly Used FS Paths"""

        # This Returns the Paths we want + "python" + "helper" + "globals.py"
        _globals_file = FileHandler.abspath(__file__)
        _globals_file = FileHandler.dirpath(_globals_file) # Removes globals.py
        _globals_file = FileHandler.dirpath(_globals_file) # Removes helper

        scripts_pwd = FileHandler.dirpath(_globals_file) # Removes python

        pytohn_scripts     = FileHandler.join([scripts_pwd, "python"])
        powershell_scripts = FileHandler.join([scripts_pwd, "powershell"])
        bash_scripts       = FileHandler.join([scripts_pwd, "bash"])
        asset_files        = FileHandler.join([scripts_pwd, "assets"])


    class patterns:
        """Regex Patterns"""
        #FROM https://github.com/geongeorge/i-hate-regex/blob/master/static/regex/data.json
        # data = []
        # for item in data:
        #     print(f"{item["id"]} = r\"{item["regex"].replace("\"", "\\\"")}\"")

        username          = r"^[a-z0-9_-]{3,15}$"
        password          = r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$ %^&*-]).{8,}$"
        email             = r"[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+"
        email_2           = r"(([^<>()\[\]\\.,;:\s@\"]+(\.[^ <> ()\[\]\\., ;:\s @ \"]+)*)|(\". + \"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))"
        phone             = r"^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$"
        ipv4              = r"(\b25[0-5]|\b2[0-4][0-9]|\b[01]?[0-9][0-9]?)(\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}"
        ipv6              = r"(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))"
        date              = r"(?:(?:31(\/|-|\.)(?:0?[13578]|1[02]))\1|(?:(?:29|30)(\/|-|\.)(?:0?[13-9]|1[0-2])\2))(?:(?:1[6-9]|[2-9]\d)?\d{2})$|^(?:29(\/|-|\.)0?2\3(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))$|^(?:0?[1-9]|1\d|2[0-8])(\/|-|\.)(?:(?:0?[1-9])|(?:1[0-2]))\4(?:(?:1[6-9]|[2-9]\d)?\d{2})"
        ascii             = r"[ -~]"
        url               = r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()!@:%_\+.~#?&\/\/=]*)"
        ssn               = r"^(?!0{3})(?!6{3})[0-8]\d{2}-(?!0{2})\d{2}-(?!0{4})\d{4}$"
        semver            = r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
        uuid              = r"^[0-9a-fA-F]{8}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{12}$"
        jira_ticket       = r"[A-Z]{2,}-\d+"
        lat_long          = r"^((\-?|\+?)?\d+(\.\d+)?),\s*((\-?|\+?)?\d+(\.\d+)?)$"
        mac_address       = r"^[a-fA-F0-9]{2}(:[a-fA-F0-9]{2}){5}$"
        url_slug          = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
        c_like_identifier = r"^[a-zA-Z_][0-9a-zA-Z_]*$"
        hyphen_word_break = r"[a-zA-Z][\-]$[\n][a-zA-Z]"
        bitcoin_address   = r"^(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}$"
        emoji             = r"(\u00a9|\u00ae|[\u2000-\u3300]|\ud83c[\ud000-\udfff]|\ud83d[\ud000-\udfff]|\ud83e[\ud000-\udfff])"
        credit_card       = r"(^4[0-9]{12}(?:[0-9]{3})?$)|(^(?:5[1-5][0-9]{2}|222[1-9]|22[3-9][0-9]|2[3-6][0-9]{2}|27[01][0-9]|2720)[0-9]{12}$)|(3[47][0-9]{13})|(^3(?:0[0-5]|[68][0-9])[0-9]{11}$)|(^6(?:011|5[0-9]{2})[0-9]{12}$)|(^(?:2131|1800|35\d{3})\d{11}$)"
        pan_from_gstin    = r"^([0][1-9]|[1-2][0-9]|[3][0-5])([a-zA-Z]{5}[0-9]{4}[a-zA-Z]{1})([1-9a-zA-Z]{1}[zZ]{1}[0-9a-zA-Z]{1})+$"
        e164_phone        = r"^\+[1-9]\d{1,14}$"
        han_unification   = r"^[\u4E00-\u9FFF\u3400-\u4DBF\u20000-\u2A6DF\u2A700-\u2B73F\u2B740-\u2B81F\u2B820-\u2CEAF\u2CEB0-\u2EBEF\u30000-\u3134F\uF900-\uFAFF\u2E80-\u2EFF\u31C0-\u31EF\u3000-\u303F\u2FF0-\u2FFF\u3300-\u33FF\uFE30-\uFE4F\uF900-\uFAFF\u2F800-\u2FA1F\u3200-\u32FF\u1F200-\u1F2FF\u2F00-\u2FDF]+$"
        port              = r"^((6553[0-5])|(655[0-2][0-9])|(65[0-4][0-9]{2})|(6[0-4][0-9]{3})|([1-5][0-9]{4})|([0-5]{0,5})|([0-9]{1,4}))$"
        doi               = r"^(10\.\d{4,5}\/[\S]+[^;,.\s])$"
        discord_username  = r"^.{3,32}#[0-9]{4}$"
        hashtag           = r"^#[^ !@#$%^&*(),.?\":{} | <>] * $"
