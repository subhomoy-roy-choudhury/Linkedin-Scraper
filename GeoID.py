# import geocoder # pip install geocoder
# g = geocoder.bing('Mountain View, CA', key='ArtgYIQKllvptIiTZw0N4rwgUfQO5WXoToKnUigkQUjn88g0JKrXJL1DZPKXgR2F')
# print(g.json)

import requests

x = requests.get("https://api.linkedin.com/v2/geoTypeahead?q=search&query=united",params={'key':'ArtgYIQKllvptIiTZw0N4rwgUfQO5WXoToKnUigkQUjn88g0JKrXJL1DZPKXgR2F'})
print(x.json)