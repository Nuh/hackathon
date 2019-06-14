from pyquery import PyQuery as pq

fbUrl = data.get('url')
name = data.get('name')

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