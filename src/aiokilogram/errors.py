from __future__ import annotations

import contextlib
from functools import wraps
from typing import (
    Any, AsyncGenerator, Awaitable, Callable,
    Optional, Sequence, TypeVar, TYPE_CHECKING, Union, cast,
)

from aiogram import types

from aiokilogram.page import MessagePage

if TYPE_CHECKING:
    from aiokilogram.messenger import MessengerInterface


class ErrorHandler:
    async def handle(self, err: Exception, messenger: MessengerInterface, user_id: str) -> bool:
        return True


class DefaultErrorHandler(ErrorHandler):
    def make_message(self, err: Exception) -> Optional[Union[MessagePage, str]]:
        return None

    async def handle(self, err: Exception, messenger: MessengerInterface, user_id: str) -> bool:
        message = self.make_message(err=err)
        if message is None:
            return True

        if isinstance(message, MessagePage):
            await messenger.send_message_page(user_id=user_id, page=message)
        else:
            assert isinstance(message, str)
            await messenger.send_text(user_id=user_id, text=message)
        return False


def _extract_user_id_from_args(handler_args: Sequence[Any], handler_kwargs: dict[str, Any]) -> str:
    obj: Union[types.Message, types.CallbackQuery]
    if handler_args:
        obj = cast(Union[types.Message, types.CallbackQuery], handler_args[0])
    else:
        assert handler_kwargs
        obj = handler_kwargs.get('event', handler_kwargs.get('query'))
        assert obj is not None

    return obj.from_user.id


@contextlib.asynccontextmanager
async def handle_errors_cm(
        error_handlers: Sequence[ErrorHandler],
        messenger: MessengerInterface,
        user_id: str,
) -> AsyncGenerator[None, None]:

    try:
        yield
    except Exception as err:
        result: bool = True
        for eh in error_handlers:
            result = await eh.handle(err=err, messenger=messenger, user_id=user_id)
            if result is False:
                break

        if result:
            raise


_FUNC_TV = TypeVar('_FUNC_TV', bound=Callable[..., Awaitable])


def handle_errors(
        error_handlers: Sequence[ErrorHandler], messenger: MessengerInterface,
) -> Callable[[_FUNC_TV], _FUNC_TV]:

    def decorator(func: _FUNC_TV) -> _FUNC_TV:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            user_id = _extract_user_id_from_args(handler_args=args, handler_kwargs=kwargs)
            async with handle_errors_cm(error_handlers=error_handlers, messenger=messenger, user_id=user_id):
                return await func(*args, **kwargs)

        return wrapper  # type: ignore

    return decorator
