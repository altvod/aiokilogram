from __future__ import annotations

import abc
from typing import Collection, Generic, Optional, Type, TypeVar, TYPE_CHECKING

import attr
from aiogram import Bot
from aiogram.dispatcher.storage import BaseStorage

from aiokilogram.settings import BaseGlobalSettings
from aiokilogram.dispatcher import KiloDispatcher

if TYPE_CHECKING:
    from aiokilogram.handler import CommandHandler


_GSETTINGS_TV = TypeVar('_GSETTINGS_TV', bound=BaseGlobalSettings)


@attr.s
class KiloBot(abc.ABC, Generic[_GSETTINGS_TV]):
    _handler_classes: Collection[Type[CommandHandler]] = attr.ib(kw_only=True, default=())
    _global_settings: _GSETTINGS_TV = attr.ib(kw_only=True)

    def register(self, bot: Bot, dispatcher: KiloDispatcher) -> None:
        for handler_cls in self._handler_classes:
            handler = handler_cls(bot=bot, global_settings=self._global_settings)
            handler.register(dispatcher=dispatcher)

    def make_fsm_storage(self) -> Optional[BaseStorage]:
        """Redefine this if you want to use FSMStorage in your bot"""
        return None

    async def run(self):
        bot = Bot(token=self._global_settings.tg_bot_token)
        try:
            fsm_storage = self.make_fsm_storage()
            dispatcher = KiloDispatcher(bot=bot, storage=fsm_storage)
            self.register(bot=bot, dispatcher=dispatcher)
            await dispatcher.start_polling()
        finally:
            await bot.close()
