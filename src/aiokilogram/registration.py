from enum import Enum
from typing import Any, Callable, NamedTuple, Optional, Sequence, Type, TypeVar, Union

from aiokilogram.action import CallbackAction, ActionParameterization


KILO_DISP_REG_INFO_ATTR = '__kilo_disp_reg_info'


class KiloDispatcherRegInfo(NamedTuple):
    reg_method_name: str
    args: Sequence[Any]
    kwargs: dict[str, Any]


_CALLABLE_TV = TypeVar('_CALLABLE_TV', bound=Callable)


def register_callback_query_handler(
        *custom_filters, state=None, run_task=None,
        action: Optional[Union[Type[CallbackAction], ActionParameterization]] = None,
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
        )
        setattr(method, KILO_DISP_REG_INFO_ATTR, reg_info)
        return method

    return decorator


def register_message_handler(
        *custom_filters, commands=None, regexp=None, content_types=None,
        state=None, run_task=None, **kwargs
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
        )
        setattr(method, KILO_DISP_REG_INFO_ATTR, reg_info)
        return method

    return decorator
