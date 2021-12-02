from __future__ import annotations

import abc
from typing import Optional, TYPE_CHECKING

import attr
import aiogram.types
import emoji

if TYPE_CHECKING:
    from aiokilogram.action import CallbackAction


@attr.s
class MessageBody:
    """Represents the text part of the message page"""

    text: str = attr.ib(kw_only=True)
    parse_mode: str = attr.ib(kw_only=True, default=aiogram.types.ParseMode.MARKDOWN_V2)


@attr.s(frozen=True)
class MessageButton(abc.ABC):
    """Base class for keyboard buttons"""

    text: Optional[str] = attr.ib(kw_only=True, default=None)
    emoji: Optional[str] = attr.ib(kw_only=True, default=None)

    @property
    def emoji_code(self) -> str:
        assert self.emoji is not None
        return emoji.emojize(f':{self.emoji}:')

    @property
    def full_text(self) -> str:
        if self.text is not None and self.emoji is not None:
            return f'{self.emoji_code} {self.text}'
        if self.text is not None:
            return self.text
        if self.emoji is not None:
            return self.emoji_code
        return ''

    @abc.abstractmethod
    def get_callback_data(self) -> str:
        raise NotImplementedError


@attr.s
class PlainMessageButton(MessageButton):
    """Plain keyboard button with callback data already prepared"""

    callback_data: str = attr.ib(kw_only=True)

    def get_callback_data(self) -> str:
        return self.callback_data


@attr.s
class ActionMessageButton(MessageButton):
    """Button with callback data generated via a ``CallbackAction``"""

    action: CallbackAction = attr.ib(kw_only=True)

    def get_callback_data(self) -> str:
        return self.action.serialize()


@attr.s
class MessageKeyboard:
    """Keyboard to be added to the message"""

    buttons: list[MessageButton] = attr.ib(kw_only=True)
    row_width: int = attr.ib(kw_only=True, default=1)


@attr.s
class MessagePage:
    """Describes the various parts and attachments of a message"""

    body: MessageBody = attr.ib(kw_only=True)
    keyboard: Optional[MessageKeyboard] = attr.ib(kw_only=True, default=None)
    disable_preview: bool = attr.ib(kw_only=True, default=False)
