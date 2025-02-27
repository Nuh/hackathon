import base64
import re
import requests
import dateparser
import urllib.request

from homeassistant.core import callback
from logging import getLogger
from pyquery import PyQuery as pq

LOGGER = getLogger(__name__)

DOMAIN = "lunch"


def normalize_name(name):
    return re.sub(r'\-', r'_', re.sub('([a-z0-9])([A-Z])', r'\1_\2', re.sub('(.)([A-Z][a-z]+)', r'\1_\2', str(name))).lower())


def get_as_base64(url):
    return base64.b64encode(requests.get(url).content)

def is_earlier_timestamp(old, new):
    if old is None:
        return True

    oldDate = dateparser.parse(old)
    newDate = dateparser.parse(new)
    return oldDate < newDate


async def async_setup(hass, config):
    @callback
    def menu_received(event):
        if event and event.data and event.data.get('name'):
            LOGGER.info("Menu received: %s", event.data['name'])
            hass.states.async_set(event.data['name'], any(event.data), event.data, True)

    hass.bus.async_listen(DOMAIN, menu_received)

    @callback
    def get_menu(call):
        friendly_name = call.data.get('name')
        fb_url = call.data.get('url')
        name = normalize_name(friendly_name)
        restaurant = pq(url=fb_url)

        menu, last_timestamp = (None, None)
        for last_post in restaurant("div").filter(".userContentWrapper"):
            if last_post is not None:
                timestamp = pq(last_post)("span").filter(".timestampContent").text()
                if (is_earlier_timestamp(last_timestamp, timestamp)):
                    title = re.sub(r'( - Posts| - Posty| \| Facebook)', r'', restaurant("title").text())
                    message = pq(last_post)("div[data-testid='post_message']").text()
                    last_timestamp = timestamp
                    images = []

                    for img in pq(last_post)("img"):
                        src = pq(img).attr("data-src")
                        if src is not None:
                            local_path = "/config/www/img/" + name + "." + str(i) + ".jpg"
                            images.append({
                                'url': src,
                                'path': local_path,
                                'script_path': re.sub(r'^/config/www', r'/local', local_path),
                                'data': "data:image/jpeg;base64," + str(get_as_base64(src), 'utf-8')
                            })
                            urllib.request.urlretrieve(src, local_path)
                            i = i+1

                    menu = {
                        'name': name,
                        'friendly-name': friendly_name,
                        'title': title,
                        'timestamp': timestamp,
                        'message': message,
                        'images': images
                    }

	if menu is not None:
            LOGGER.info("Downloaded menu for: %s (%s)", menu.get('name'), menu.get('friendly_name'))

            hass.bus.fire(name, menu)
            hass.bus.fire(DOMAIN, menu)

    # Register our service with Home Assistant.
    hass.services.async_register(DOMAIN, 'get_menu', get_menu)

    # Return boolean to indicate that initialization was successfully.
    return True
