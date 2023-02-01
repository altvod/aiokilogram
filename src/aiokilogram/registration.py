from typing import Any, Callable, Optional, Sequence, Type, TypeVar, Union

import attr

from aiokilogram.action import CallbackAction, ActionParameterization
from aiokilogram.errors import ErrorHandler


KILO_DISP_REG_INFO_ATTR = '__kilo_disp_reg_info'


@attr.s(frozen=True)
class KiloDispatcherRegInfo:
    reg_method_name: str = attr.ib(kw_only=True)
    args: Sequence[Any] = attr.ib(kw_only=True)
    kwargs: dict[str, Any] = attr.ib(kw_only=True)
    error_handler: Optional[ErrorHandler] = attr.ib(kw_only=True, default=None)


_CALLABLE_TV = TypeVar('_CALLABLE_TV', bound=Callable)


def register_callback_query_handler(
        *custom_filters, state=None, run_task=None,
        action: Optional[Union[Type[CallbackAction], ActionParameterization]] = None,
        error_handler: Optional[ErrorHandler] = None,
        **kwargs,
) -> Callable[[_CALLABLE_TV], _CALLABLE_TV]:
    """
    Decorator for registering a kilo bot method as a callback query handler
    """

    def decorator(method: _CALLABLE_TV) -> _CALLABLE_TV:
        reg_info = KiloDispatcherRegInfo(
            reg_method_name='register_callback_query_handler',
            args=custom_filters,
            kwargs=dict(
                state=state, run_task=run_task, action=action,
                **kwargs,
            ),
            error_handler=error_handler,
        )
        setattr(method, KILO_DISP_REG_INFO_ATTR, reg_info)
        return method

    return decorator


def register_message_handler(
        *custom_filters, commands=None, regexp=None, content_types=None,
        state=None, run_task=None,
        error_handler: Optional[ErrorHandler] = None,
        **kwargs,
) -> Callable[[_CALLABLE_TV], _CALLABLE_TV]:
    """
    Decorator for registering a kilo bot method as message handler
    """

    def decorator(method: _CALLABLE_TV) -> _CALLABLE_TV:
        reg_info = KiloDispatcherRegInfo(
            reg_method_name='register_message_handler',
            args=custom_filters,
            kwargs=dict(
                commands=commands, regexp=regexp, content_types=content_types,
                state=state, run_task=run_task,
                **kwargs,
            ),
            error_handler=error_handler,
        )
        setattr(method, KILO_DISP_REG_INFO_ATTR, reg_info)
        return method

    return decorator
