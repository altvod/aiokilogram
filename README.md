# aiokilogram

Convenience tools and wrappers for `aiogram`,
the asynchronous Telegram Bot API framework.


## Installation

```bash
pip install aiokilogram
```


## Basic Examples

### Class-Based Command Handlers

The `aiokilogram` toolkit is centered around the notion of class-based
command handlers. Basically this means that you can group several commands
as methods in a class and assign them to message and callback patterns
at class level.

Handler classes look something like this:

```python
from aiokilogram.handler import CommandHandler

class TestCommandHandler(CommandHandler):
    async def test_handler(self, event) -> None:
        await self.send_text(user_id=event.from_user.id, text=f'This is a test reply')
        
    # other related commands go here

    def register(self, dispatcher) -> None:
        dispatcher.register_message_handler(self.test_handler, commands={'hello'})
        # register other commands here
```

The whole bot application will then be run like this:
```python
import asyncio
import os
from aiokilogram.bot import KiloBot
from aiokilogram.settings import BaseGlobalSettings

class TestBot(KiloBot):
    def register(self, bot, dispatcher) -> None:
        TestCommandHandler(global_settings=self._global_settings, bot=bot).register(dispatcher)
        # other command handlers can be added here

def run_bot():
    bot = TestBot(global_settings=BaseGlobalSettings(
        tg_bot_token=os.environ['TG_BOT_TOKEN']
    ))
    asyncio.run(bot.run())

if __name__ == '__main__':
    run_bot()
```

For more info you can take a look at a [simple boilerplate bot](boilerplate/simple.py)

Set the `TG_BOT_TOKEN` env variable to run it.


### Action Buttons

The package also provides a simplified mechanism of using buttons and 
binding handlers to their callbacks.
This is useful when you want your buttons to contain a combination of
several parameters and don't want to implement their serialization,
deserialization and callback bindings each time.

The idea is simple.

1. Define an action (a `CallbackAction` subclass) using a combination of fields:
```python
from enum import Enum
from aiokilogram.action import CallbackAction, StringActionField, EnumActionField

class ActionType(Enum):
    show_recipe = 'show_recipe'
    like_recipe = 'like_recipe'

class SingleRecipeAction(CallbackAction):
    action_type = EnumActionField(enum_cls=ActionType)
    recipe_title = StringActionField()
```

2. Create a page containing action buttons:
```python
from aiokilogram.page import ActionMessageButton, MessagePage, MessageBody, MessageKeyboard

page = MessagePage(
    body=MessageBody(text='Main Recipe Menu'),
    keyboard=MessageKeyboard(buttons=[
        ActionMessageButton(
            text='Button Text',
            action=SingleRecipeAction(
                action_type=ActionType.show_recipe,
                recipe_title='Fantastic Menemen',
            ),
        ),
        # ...
    ])
)
```

3. Send it as a response to some command in your handler class:
```python
    await self.send_message_page(user_id=event.from_user.id, page=page)
```

4. Bind a method to this action class in the `register` method of the handler class:
```python
    dispatcher.register_callback_query_handler(
        self.action_handler_method, action=SingleRecipeAction,
    )
```
or you can be more precise and limit the binding to specific values
of the action's fields:
```python
    dispatcher.register_callback_query_handler(
        self.action_handler_method,
        action=ListRecipesAction.when(action_type=ActionType.like_recipe),
    )
```

5. Deserialize the action parameters in the handler method:
```python
action = SingleRecipeAction.deserialize(query.data)
if 'soup' in action.recipe_title.lower():
    do_soup_stuff()  # whatever
```


See [boilerplate bot with buttons](boilerplate/button.py)

Set the `TG_BOT_TOKEN` env variable to run it.


## Links

Homepage on GitHub: https://github.com/altvod/aiokilogram

Project's page on PyPi: https://pypi.org/project/aiokilogram/

`aiogram`'s homepage on GitHub: https://github.com/aiogram/aiogram

Telegram Bot API: https://core.telegram.org/bots/api
