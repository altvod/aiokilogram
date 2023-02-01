from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from aiokilogram.page import MessagePage


class MessengerInterface:
    # @abc.abstractmethod
    async def send_text(self, user_id: str, text: str) -> None:
        raise NotImplementedError

    # @abc.abstractmethod
    async def send_message_page(self, user_id: str, page: MessagePage) -> None:
        raise NotImplementedError
