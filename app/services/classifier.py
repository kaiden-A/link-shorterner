import re


def classify_source(referer: str | None, utm_source: str | None = None) -> str | None:
    if utm_source:
        return utm_source.lower().strip()

    if not referer:
        return None

    referer = referer.lower()

    patterns = {
        "instagram": r"(?:www\.)?(?:l\.)?instagram\.com",
        "facebook": r"(?:www\.)?(?:l|m|mbasic)?\.?facebook\.com",
        "threads": r"(?:www\.)?threads\.net",
        "twitter": r"(?:www\.)?(?:t\.co|twitter\.com|x\.com)",
        "whatsapp": r"(?:www\.)?(?:api\.)?whatsapp\.com",
        "telegram": r"(?:www\.)?(?:t\.me|telegram\.(?:me|org))",
        "youtube": r"(?:www\.)?youtube\.com",
        "linkedin": r"(?:www\.)?linkedin\.com",
        "discord": r"(?:www\.)?discord\.(?:com|gg)",
        "reddit": r"(?:www\.)?reddit\.com",
        "tiktok": r"(?:www\.)?tiktok\.com",
        "pinterest": r"(?:www\.)?pinterest\.",
        "snapchat": r"(?:www\.)?snapchat\.com",
    }

    for source, pattern in patterns.items():
        if re.search(pattern, referer):
            return source

    return "other"


def parse_user_agent(user_agent: str | None) -> tuple[str | None, str | None, str | None]:
    if not user_agent:
        return None, None, None

    ua = user_agent.lower()

    os = None
    if "windows" in ua:
        os = "Windows"
    elif "mac os" in ua or "macintosh" in ua:
        os = "macOS"
    elif "linux" in ua and "android" not in ua:
        os = "Linux"
    elif "android" in ua:
        os = "Android"
    elif "ios" in ua or "iphone" in ua or "ipad" in ua or "ipod" in ua:
        os = "iOS"
    elif "cros" in ua:
        os = "ChromeOS"

    browser = None
    if "opr" in ua or "opera" in ua:
        browser = "Opera"
    elif "edg" in ua or "edge" in ua:
        browser = "Edge"
    elif "chrome" in ua and "chromium" not in ua:
        browser = "Chrome"
    elif "firefox" in ua and "seamonkey" not in ua:
        browser = "Firefox"
    elif "safari" in ua and "chrome" not in ua:
        browser = "Safari"
    elif "chromium" in ua:
        browser = "Chromium"

    device_type = None
    if "mobile" in ua or "android" in ua and "tablet" not in ua or "iphone" in ua:
        device_type = "mobile"
    elif "tablet" in ua or "ipad" in ua or "kindle" in ua:
        device_type = "tablet"
    else:
        device_type = "desktop"

    return device_type, browser, os