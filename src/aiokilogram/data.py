"""
Tools for accessing data within the state storage
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator, TYPE_CHECKING, Type, TypeVar

from aiokilogram.action import CallbackAction

if TYPE_CHECKING:
    from aiogram.dispatcher import FSMContext


KEY_STATE = '__state_data__'
KEY_CURRENT_ACTION = '__current_action__'
KEY_ACTION_DATA = '__action_data__'


@asynccontextmanager
async def get_state_data(state: FSMContext, clear_state: bool = False) -> AsyncGenerator[dict, None]:
    async with state.proxy() as data_proxy:
        if KEY_STATE not in data_proxy:
            data_proxy[KEY_STATE] = {}
        state_data = data_proxy[KEY_STATE]
        assert isinstance(state_data, dict)
        yield state_data
        if clear_state:
            state_data.clear()


@asynccontextmanager
async def get_action_data(state: FSMContext, clear_state: bool = False) -> AsyncGenerator[dict, None]:
    async with get_state_data(state=state, clear_state=clear_state) as state_data:
        if KEY_ACTION_DATA not in state_data:
            state_data[KEY_ACTION_DATA] = {}
        action_data = state_data[KEY_ACTION_DATA]
        assert isinstance(action_data, dict)
        yield action_data


_ACTION_TV = TypeVar('_ACTION_TV', bound=CallbackAction)


async def load_current_action_from_state(
        state: FSMContext, action_cls: Type[_ACTION_TV], clear_state: bool = False
) -> _ACTION_TV:
    async with get_action_data(state, clear_state=clear_state) as action_data:
        current_action_cb_data = action_data[KEY_CURRENT_ACTION]
        action = action_cls.deserialize(current_action_cb_data)
        return action


async def save_current_action_to_state(state: FSMContext, action: CallbackAction) -> None:
    current_action_cb_data = action.serialize()
    async with get_action_data(state) as action_data:
        action_data[KEY_CURRENT_ACTION] = current_action_cb_data
