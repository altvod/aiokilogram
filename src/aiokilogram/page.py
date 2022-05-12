from __future__ import annotations

import abc
from typing import Iterable, Optional, TYPE_CHECKING, Union

import attr
import aiogram.types
from emoji.core import emojize

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
        return emojize(f':{self.emoji.strip(":")}:')

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


def simple_page(
        text: str, buttons: Iterable[Union[tuple[str, CallbackAction], tuple[str, CallbackAction, str]]] = (),
) -> MessagePage:
    button_objs: list[MessageButton] = []
    for button_text, button_action, *extra in buttons:
        emoji: Optional[str] = None
        if extra:
            emoji = extra[0]
        button = ActionMessageButton(action=button_action, text=button_text, emoji=emoji)
        button_objs.append(button)
    page = MessagePage(
        body=MessageBody(text=text),
        keyboard=MessageKeyboard(buttons=button_objs),
    )
    return page
