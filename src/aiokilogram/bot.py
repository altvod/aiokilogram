from __future__ import annotations

import abc
from typing import Generic, Optional, TypeVar

import attr
from aiogram import Bot
from aiogram.dispatcher.storage import BaseStorage

from aiokilogram.settings import BaseGlobalSettings
from aiokilogram.dispatcher import KiloDispatcher


_GSETTINGS_TV = TypeVar('_GSETTINGS_TV', bound=BaseGlobalSettings)


@attr.s
class KiloBot(abc.ABC, Generic[_GSETTINGS_TV]):
    _global_settings: _GSETTINGS_TV = attr.ib(kw_only=True)

    @abc.abstractmethod
    def register(self, bot: Bot, dispatcher: KiloDispatcher) -> None:
        raise NotImplementedError

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
