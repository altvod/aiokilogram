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

A simplistic bit will look something like this:

```python
import asyncio
import os
from aiokilogram.bot import KiloBot
from aiokilogram.settings import BaseGlobalSettings
from aiokilogram.handler import CommandHandler
from aiokilogram.registration import register_message_handler

class TestCommandHandler(CommandHandler):
    @register_message_handler(commands={'hello'})
    async def test_handler(self, event) -> None:
        await self.send_text(user_id=event.from_user.id, text=f'This is a test reply')

def run_bot():
    bot = KiloBot(
        global_settings=BaseGlobalSettings(tg_bot_token=os.environ['TG_BOT_TOKEN']),
        handler_classes=[TestCommandHandler],
    )
    asyncio.run(bot.run())

if __name__ == '__main__':
    run_bot()
```

For more info you can take a look at a [boilerplate bot with buttons](boilerplate/button.py)
and [simple boilerplate bot](boilerplate/simple.py)

Set the `TG_BOT_TOKEN` env variable to run them.


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

4. Define and register a handler method for this action where you deserialize the 
   action parameters and somehow use them in your logic:
```python
class MyHandler(CommandHandler):
    @register_callback_query_handler(action=SingleRecipeAction)
    async def do_single_recipe_action(self, query: types.CallbackQuery) -> None:
        action = SingleRecipeAction.deserialize(query.data)
        if 'soup' in action.recipe_title.lower():
            do_soup_stuff()  # whatever
        # ...
```
or you can be more precise and limit the binding to specific values
of the action's fields:
```python
    @register_callback_query_handler(
        action=SingleRecipeAction.when(action_type=ActionType.like_recipe),
    )
```


See [boilerplate bot with buttons](boilerplate/button.py)

Set the `TG_BOT_TOKEN` env variable to run it.


### Error handling

Generic error (exception) handling in bots can be implemented via `ErrorHandler`s
at class or method level.

First, define an error handler:

```python
from aiokilogram.errors import DefaultErrorHandler

class MyErrorHandler(DefaultErrorHandler):
    def make_message(self, err: Exception):
        # Any custom logic can go here.
        # This method can return either a `str`, a `MessagePage` or `None`.
        # In case of `None` no message is sent and the exception is re-raised.
        return 'This is my error message'
```

Then add it either to the message handler class:

```python
class MyCommandHandler(CommandHandler):
    error_handler = MyErrorHandler()
```

to handle errors in all methods registered via the
`register_message_handler` and `register_callback_query_handler` decorators.

Or you can do it at method-level:

```python
    @register_message_handler(commands={'my_command'}, error_handler=MyErrorHandler())
    async def my_command_handler(self, event: types.Message) -> None:
        pass  # do whatever you do...
```

See [boilerplate bot with error handling](boilerplate/errors.py)

Set the `TG_BOT_TOKEN` env variable to run it.


## Links

Homepage on GitHub: https://github.com/altvod/aiokilogram

Project's page on PyPi: https://pypi.org/project/aiokilogram/

`aiogram`'s homepage on GitHub: https://github.com/aiogram/aiogram

Telegram Bot API: https://core.telegram.org/bots/api
