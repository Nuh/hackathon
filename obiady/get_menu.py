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

print(restaurant("title").text())
print("timestamp: " + pq(lastPost)("span").filter(".timestampContent").text())
print("description: " + pq(lastPost)("div[data-testid='post_message'] ").text())
# print("img: " + pq(lastPost)("img").attr("data-src"))	
print("imgages: ")
images = pq(lastPost)("img")
for img in images:
	dataSrc = pq(img).attr("data-src")
	if dataSrc is not None:
		menu['img'].append(pq(img).attr("data-src"))
		print(pq(img).attr("data-src"))	

hass.bus.fire(name, menu)