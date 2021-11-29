import re
from typing import Optional, Type, Union

from aiogram import Dispatcher

from aiokilogram.action import CallbackAction, ActionParameterization


class KiloDispatcher(Dispatcher):
    """
    Override some of the methods to add a bit more functionality.
    """

    def register_callback_query_handler(
            self, callback, *custom_filters, state=None, run_task=None,
            action: Optional[Union[Type[CallbackAction], ActionParameterization]] = None,
            **kwargs,
    ):  # type: ignore

        if action is not None:
            if kwargs.get('regexp') is not None:
                raise ValueError('Cannot combine parameters "regexp" and "action"')
            kwargs['regexp'] = re.compile(action.get_pattern())

        return super().register_callback_query_handler(
            callback, *custom_filters,
            state=state, run_task=run_task, **kwargs,
        )

    def callback_query_handler(
            self, *custom_filters, state=None, run_task=None,
            action: Optional[Union[Type[CallbackAction], ActionParameterization]] = None,
            **kwargs,
    ):  # type: ignore

        if action is not None:
            if kwargs.get('regexp') is not None:
                raise ValueError('Cannot combine parameters "regexp" and "action"')
            kwargs['regexp'] = re.compile(action.get_pattern())

        return super().register_callback_query_handler(
            *custom_filters, state=state, run_task=run_task, **kwargs,
        )
