import asyncio
import os
import re

from aiogram import Bot, types

from aiokilogram.bot import KiloBot
from aiokilogram.settings import BaseGlobalSettings
from aiokilogram.dispatcher import KiloDispatcher
from aiokilogram.handler import CommandHandler


class ToplevelCommandHandler(CommandHandler):
    """Handles top-level commands"""

    async def hello_handler(self, event: types.Message) -> None:
        await self.send_text(
            user_id=event.from_user.id,
            text=f'Hello, {event.from_user.get_mention(as_html=True)}, and and thanks for all the fish!'
        )

    async def menu_handler(self, event: types.Message) -> None:
        await self.send_text(user_id=event.from_user.id, text=f'Main Menu: ...')

    def register(self, dispatcher: KiloDispatcher) -> None:
        dispatcher.register_message_handler(self.hello_handler, commands={'hello'})
        dispatcher.register_message_handler(self.hello_handler, commands={'menu'})


class CabbageCommandHandler(CommandHandler):
    """Handles cabbage-specific commands"""

    _COOK_RE = re.compile(r'/cabbage_cook_(?P<what>.*)')

    async def grow_cabbage(self, event: types.Message) -> None:
        await self.send_text(user_id=event.from_user.id, text=f'Planted some cabbage')

    async def cook_something(self, event: types.Message) -> None:
        what = self._COOK_RE.match(event.text).group('what')
        await self.send_text(user_id=event.from_user.id, text=f'Cooking {what} from cabbage')

    def register(self, dispatcher: KiloDispatcher) -> None:
        dispatcher.register_message_handler(self.grow_cabbage, commands={'cabbage_grow'})
        dispatcher.register_message_handler(self.cook_something, regexp=self._COOK_RE)


class SimpleBot(KiloBot):
    def register(self, bot: Bot, dispatcher: KiloDispatcher) -> None:
        ToplevelCommandHandler(global_settings=self._global_settings, bot=bot).register(dispatcher)
        CabbageCommandHandler(global_settings=self._global_settings, bot=bot).register(dispatcher)


def run_bot():
    bot = SimpleBot(global_settings=BaseGlobalSettings(tg_bot_token=os.environ['TG_BOT_TOKEN']))
    asyncio.run(bot.run())


if __name__ == '__main__':
    run_bot()
