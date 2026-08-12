import logging

logger = logging.getLogger(__name__)

from rom24 import handler_game
from rom24 import merc
from rom24 import interp
from rom24 import state_checks
from rom24 import api


def do_weather(ctx):
    ch = ctx.ch
    argument = ctx.arg
    sky_look = ["cloudless", "cloudy", "rainy", "lit by flashes of lightning"]
    if not state_checks.IS_OUTSIDE(ch):
        ch.send("You can't see the weather indoors.\n")
        return

    ch.send(
        "The sky is %s and %s.\n"
        % (
            sky_look[handler_game.weather_info.sky],
            "a warm southerly breeze blows"
            if handler_game.weather_info.change >= 0
            else "a cold northern gust blows",
        )
    )
    return


api.register("weather", do_weather, pos=merc.POS_RESTING, level=0, log=merc.LOG_NORMAL, show=1)
