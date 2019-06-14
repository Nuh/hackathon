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
        if event and event.data and event.data.id:
            LOGGER.info("Menu received: %s", event.data.id)
            hass.states.async_set(event.data.id, any(event.data), event.data, True)

    hass.bus.async_listen(DOMAIN, menu_received)

    @callback
    def get_menu(call):
        friendly_name = call.data.get('name')
        fb_url = call.data.get('url')
        name = normalize_name(friendly_name)

        restaurant = pq(url=fb_url)
        last_post = restaurant("div").filter(".userContentWrapper")[0]
        if last_post:
            title = re.sub(r' - Posty | Facebook', r'', restaurant("title").text())
            images = []
            LOGGER.info("Downloaded menu for: %s (%s)", title, friendly_name)

            for img in pq(last_post)("img"):
                src = pq(img).attr("data-src")
                if src is not None:
                    images.append({'url': src, 'data': "data:image/jpeg;base64," + str(get_as_base64(src), 'utf-8')})

            menu = {'name': name, 'friendly-name': friendly_name, 'title': title, 'timestamp': pq(last_post)("span").filter(".timestampContent").text(), 'text': pq(last_post)("div[data-testid='post_message'] ").text()}
            hass.bus.fire(name, menu)
            hass.bus.fire(DOMAIN, menu)
    

    # Register our service with Home Assistant.
    hass.services.async_register(DOMAIN, 'get_menu', get_menu)

    # Return boolean to indicate that initialization was successfully.
    return True