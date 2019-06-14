from homeassistant.core import callback
from pyquery import PyQuery as pq

# The domain of your component. Should be equal to the name of your component.
DOMAIN = "lunch"

async def async_setup(hass, config):
   
    @callback
    def get_menu(call):
    	fbUrl = call.data.get('url')
    	name = call.data.get('name')

    	restaurant = pq(url=fbUrl)
    	lastPost = restaurant("div").filter(".userContentWrapper")[0]

    	menu = {}
    	menu['name'] = restaurant("title").text()
    	menu['timestamp'] = pq(lastPost)("span").filter(".timestampContent").text()
    	menu['text'] = pq(lastPost)("div[data-testid='post_message'] ").text()
    	menu['img'] = []

    	images = pq(lastPost)("img")
    	for img in images:
    		dataSrc = pq(img).attr("data-src")
    		if dataSrc is not None:
    			menu['img'].append("data:image/jpeg;base64," + str(get_as_base64(dataSrc), 'utf-8'))
    			

    	hass.bus.fire(name, menu)    
    

    # Register our service with Home Assistant.
    hass.services.async_register(DOMAIN, 'get_menu', get_menu)

    # Return boolean to indicate that initialization was successfully.
    return True