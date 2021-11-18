import attr


@attr.s(frozen=True)
class BaseGlobalSettings:
    """
    Global bot application settings.

    Should be inherited for customization.
    """

    # Telegram API token
    tg_bot_token: str = attr.ib(kw_only=True)
