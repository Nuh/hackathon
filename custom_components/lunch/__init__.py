from homeassistant.core import callback
from logging import getLogger
from pyquery import PyQuery as pq
import base64
import re
import requests

LOGGER = getLogger(__name__)

DOMAIN = "lunch"

def normalize_name(name):
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', re.sub('(.)([A-Z][a-z]+)', r'\1_\2', str(name))).lower()

def get_as_base64(url):
    return base64.b64encode(requests.get(url).content)

async def async_setup(hass, config):

    @callback
    def menu_received(event):
        LOGGER.info("Menu received: %s", event.data)
        # hass.states.async_set(event.attributes.id, event.attributes)

    hass.bus.async_listen(DOMAIN, menu_received)

    @callback
    def get_menu(call):
        fbUrl = call.data.get('url')
        name = call.data.get('name')
        id = normalize_name(name)

        restaurant = pq(url=fbUrl)
        lastPost = restaurant("div").filter(".userContentWrapper")[0]

        menu = {}
        menu['id'] = id
        menu['name'] = restaurant("title").text()
        menu['timestamp'] = pq(lastPost)("span").filter(".timestampContent").text()
        menu['text'] = pq(lastPost)("div[data-testid='post_message'] ").text()
        menu['img'] = []

        images = pq(lastPost)("img")
        for img in images:
            dataSrc = pq(img).attr("data-src")
            if dataSrc is not None:
                menu['img'].append("data:image/jpeg;base64," + str(get_as_base64(dataSrc), 'utf-8'))
        LOGGER.info("Downloaded menu for: %s", id)
        hass.bus.fire(id, menu)
        hass.bus.fire(DOMAIN, menu)
    

    # Register our service with Home Assistant.
    hass.services.async_register(DOMAIN, 'get_menu', get_menu)

    # Return boolean to indicate that initialization was successfully.
    return True