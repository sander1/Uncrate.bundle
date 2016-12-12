TITLE = 'Uncrate'
ICON = 'icon-default.jpg'
UNCRATE_URL = 'http://uncrate.com/tv/'

###################################################################################################
def Start():

	ObjectContainer.title1 = TITLE
	HTTP.CacheTime = 300
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36'

###################################################################################################
@handler('/video/uncrate', TITLE, thumb=ICON)
def MainMenu():

	return LatestList(page=1)

###################################################################################################
@route('/video/uncrate/latest/{page}', page=int, allow_sync=True)
def LatestList(page):

	oc = ObjectContainer(title2="Latest Videos")
	result = {}

	@parallelize
	def GetVideos():

		url = UNCRATE_URL
		if page > 1:
			url = '%s%d/' % (url, page)

		html = HTML.ElementFromURL(url)
		videos = html.xpath('//li[contains(@class, "article")]')

		for num in range(len(videos)):
			video = videos[num]

			@task
			def GetVideo(num=num, result=result, video=video):
				try:
					uncrate_url = video.xpath('./div/a/@href')[0]
					uncrate_html = HTML.ElementFromURL(uncrate_url, cacheTime=CACHE_1WEEK)
					url = uncrate_html.xpath('//iframe[@data-src]/@data-src')[0]
					video = URLService.MetadataObjectForURL(url)

					if video is not None:
						result[num] = video
				except:
					pass

	keys = result.keys()
	keys.sort()

	for key in keys:
		oc.add(result[key])

	oc.add(NextPageObject(key=Callback(LatestList, page=page+1), title="More Videos..."))

	return oc
