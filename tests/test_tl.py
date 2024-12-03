import pytest
from aiogram import Bot
from utils.tl_utils import check_subscription
from config import settings


@pytest.fixture
async def get_bot() -> Bot:
    yield Bot(settings.TOKEN)


async def test_check_subscription_link(
    get_bot, user_id: int = 1713121214, link: str = "2494342292"
):
    is_subscribed = await check_subscription(get_bot, user_id, link)

    if is_subscribed:
        assert is_subscribed is True
    else:
        with pytest.raises(Exception, match="User is not subscribed"):
            raise Exception("User is not subscribed")


async def test_check_subscription_inner_id(
    get_bot, user_id: int = 1713121214, link: str = "-1002452112688"
):
    is_subscribed = await check_subscription(get_bot, user_id, link)

    if is_subscribed:
        assert is_subscribed is True
    else:
        with pytest.raises(Exception, match="User is not subscribed"):
            raise Exception("User is not subscribed")
