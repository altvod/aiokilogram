from __future__ import annotations

import abc
from typing import Generic, Optional, TYPE_CHECKING, TypeVar

import attr
from aiogram import types
from aiogram import Bot, Dispatcher

from aiokilogram.settings import BaseGlobalSettings

if TYPE_CHECKING:
    from aiokilogram.page import MessagePage


_GSETTINGS_TV = TypeVar('_GSETTINGS_TV', bound=BaseGlobalSettings)


@attr.s
class CommandHandler(abc.ABC, Generic[_GSETTINGS_TV]):
    """
    Base for all command-handling classes.
    Can host multiple handler methods,
    all of which must be registered in the ``register`` method.
    """

    _global_settings: _GSETTINGS_TV = attr.ib(kw_only=True)
    _bot: Bot = attr.ib(kw_only=True)

    @abc.abstractmethod
    def register(self, dispatcher: Dispatcher) -> None:
        """
        Handler registration happens here.

        Must be defined explicitly in each subclass.
        """
        raise NotImplementedError

    async def respond_with_text(self, event: types.Message, text: str) -> None:
        await self.send_text(user_id=event.from_user.id, text=text)

    async def send_text(self, user_id: str, text: str) -> None:
        await self._bot.send_message(
            user_id, text=text,
            parse_mode=types.ParseMode.HTML,
        )

    async def send_message_page(self, user_id: str, page: MessagePage) -> None:
        keyboard_markup: Optional[types.InlineKeyboardMarkup] = None
        if page.keyboard:
            keyboard_markup = types.InlineKeyboardMarkup(row_width=page.keyboard.row_width)
            for button in page.keyboard.buttons:
                button = types.InlineKeyboardButton(
                    text=button.full_text,
                    callback_data=button.get_callback_data(),
                )
                keyboard_markup.add(button)

        text = page.body.text
        parse_mode = page.body.parse_mode
        await self._bot.send_message(
            user_id,
            text=text,
            parse_mode=parse_mode,
            reply_markup=keyboard_markup,
            disable_web_page_preview=page.disable_preview,
        )
