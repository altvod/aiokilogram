import asyncio
import os
from enum import Enum

from aiogram import Bot, types

from aiokilogram.bot import KiloBot
from aiokilogram.settings import BaseGlobalSettings
from aiokilogram.dispatcher import KiloDispatcher
from aiokilogram.handler import CommandHandler
from aiokilogram.action import (
    CallbackAction, StringActionField, EnumActionField,
)
from aiokilogram.page import (
    simple_page, ActionMessageButton, MessagePage, MessageBody, MessageKeyboard,
)


class ActionType(Enum):
    show_recipe = 'show_recipe'
    like_recipe = 'like_recipe'


class RecipeOwner(Enum):
    daniel = 'daniel'
    angela = 'angela'


class SingleRecipeAction(CallbackAction):
    action_type = EnumActionField(enum_cls=ActionType)
    recipe_title = StringActionField()


class ListRecipesAction(CallbackAction):
    owner = EnumActionField(enum_cls=RecipeOwner)


class RecipeCommandHandler(CommandHandler):
    """Handles recipe commands"""

    async def do_single_recipe_action(self, query: types.CallbackQuery) -> None:
        action = SingleRecipeAction.deserialize(query.data)
        if action.action_type == ActionType.show_recipe:
            page = simple_page(
                text=rf'Here is the "{action.recipe_title}" recipe: \.\.\.',
                buttons=(
                    ('Like', action.clone(action_type=ActionType.like_recipe), 'thumbs_up'),
                )
            )
        elif action.action_type == ActionType.like_recipe:
            # self.like_recipe(title=action.recipe_title)
            page = simple_page(
                text=rf'Liked the "{action.recipe_title}" recipe',
            )
        else:
            raise ValueError(f'Unsupported action: {action.action_type}')

        await self.send_message_page(user_id=query.from_user.id, page=page)

    def _make_recipe_list_page(self, owner: RecipeOwner) -> MessagePage:
        """Using the `simple_page` shortcut function here"""

        return simple_page(
            text=f'List of recipes from {owner.name.capitalize()}',
            buttons=[
                ('Menemen', SingleRecipeAction(
                    action_type=ActionType.show_recipe, recipe_title='Fantastic Menemen')),
                ('Cheeseburger', SingleRecipeAction(
                    action_type=ActionType.show_recipe, recipe_title='Classic Cheeseburger')),
                ('Poke', SingleRecipeAction(
                    action_type=ActionType.show_recipe, recipe_title='Salmon Poke')),
            ]
        )

    async def list_recipes_of_angela(self, query: types.CallbackQuery) -> None:
        await self.send_message_page(
            user_id=query.from_user.id,
            page=self._make_recipe_list_page(owner=RecipeOwner.angela)
        )

    async def list_recipes_of_daniel(self, query: types.CallbackQuery) -> None:
        await self.send_message_page(
            user_id=query.from_user.id,
            page=self._make_recipe_list_page(owner=RecipeOwner.daniel)
        )

    async def recipe_menu(self, event: types.Message) -> None:
        """Compiling a page manually"""

        page = MessagePage(
            body=MessageBody(text='Main Recipe Menu'),
            keyboard=MessageKeyboard(buttons=[
                ActionMessageButton(
                    text='Angela\'s Recipes',
                    action=ListRecipesAction(owner=RecipeOwner.angela),
                ),
                ActionMessageButton(
                    text='Daniel\'s Recipes',
                    action=ListRecipesAction(owner=RecipeOwner.daniel),
                ),
            ])
        )
        await self.send_message_page(user_id=event.from_user.id, page=page)

    def register(self, dispatcher: KiloDispatcher) -> None:
        dispatcher.register_callback_query_handler(
            self.do_single_recipe_action, action=SingleRecipeAction,
        )
        dispatcher.register_callback_query_handler(
            self.list_recipes_of_angela,
            action=ListRecipesAction.when(owner=RecipeOwner.angela),
        )
        dispatcher.register_callback_query_handler(
            self.list_recipes_of_daniel,
            action=ListRecipesAction.when(owner=RecipeOwner.daniel),
        )
        dispatcher.register_message_handler(
            self.recipe_menu, commands={'recipe_menu'},
        )


class ButtonBot(KiloBot):
    def register(self, bot: Bot, dispatcher: KiloDispatcher) -> None:
        RecipeCommandHandler(global_settings=self._global_settings, bot=bot).register(dispatcher)


def run_bot():
    bot = ButtonBot(global_settings=BaseGlobalSettings(tg_bot_token=os.environ['TG_BOT_TOKEN']))
    asyncio.run(bot.run())


if __name__ == '__main__':
    run_bot()
