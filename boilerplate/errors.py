import asyncio
import os
from typing import Optional, Union

from aiogram import types

from aiokilogram.bot import KiloBot
from aiokilogram.settings import BaseGlobalSettings
from aiokilogram.handler import CommandHandler
from aiokilogram.errors import DefaultErrorHandler
from aiokilogram.page import MessagePage, simple_page
from aiokilogram.registration import register_message_handler


class MainErrorHandler(DefaultErrorHandler):
    def make_message(self, err: Exception) -> Optional[Union[MessagePage, str]]:
        return f'This is the main error message about {type(err).__name__}'


class CustomErrorHandler(DefaultErrorHandler):
    def make_message(self, err: Exception) -> Optional[Union[MessagePage, str]]:
        return simple_page(text=f'This is the custom error message about {type(err).__name__}')


class ErrorHandlingCommandHandler(CommandHandler):
    """Handles errors raised by methods"""

    error_handler = MainErrorHandler()

    @register_message_handler(commands={'main'})
    async def main_error_raiser(self, event: types.Message) -> None:
        raise RuntimeError

    @register_message_handler(commands={'custom'}, error_handler=CustomErrorHandler())
    async def custom_error_raiser(self, event: types.Message) -> None:
        raise RuntimeError


def run_bot():
    bot = KiloBot(
        global_settings=BaseGlobalSettings(tg_bot_token=os.environ['TG_BOT_TOKEN']),
        handler_classes=[ErrorHandlingCommandHandler],
    )
    asyncio.run(bot.run())


if __name__ == '__main__':
    run_bot()
