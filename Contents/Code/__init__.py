#
	#
		#
			# HAWAII NEWS CHANNELS FOR PLEX
				# VERSION 1.2 | 2017-2018
			# BY [OSCAR KAMEOKA] ~ FOR THE PEOPLE OF HAWAII ~ {WWW.KITSUNE.WORK}
		#
	#
#

# IMPORTS
#import requests

# GLOBAL VARIABLES
NAME 			= 'HAWAII NEWS'
PREFIX 			= '/video/HawaiiNews'
VERSION 		= '1.1'
CHANNELS 		= 'http://projects.kitsune.work/aTV/HNC/channels.json'
ALERTS 			= 'http://projects.kitsune.work/aTV/HNC/alerts.json'
ICON 			= 'icon-default.png'
ART    			= 'art-default.jpg'

####################################################################################

def Start():
	ObjectContainer.title1 	= NAME
	ObjectContainer.art 	= R(ART)
	DirectoryObject.art 	= R(ART)
	VideoClipObject.art 	= R(ART)

	# HTTP SETTINGS
	HTTP.Headers['User-Agent']    = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/604.3.5 (KHTML, like Gecko) Version/11.0.1 Safari/604.3.5'
	HTTP.Headers['Cache-Control'] = 'no-cache'
	HTTP.CacheTime                = -1
	HTTP.ClearCache()

####################################################################################

@handler(PREFIX, NAME, ICON)
def MainMenu():
	load_JSON()

	oc = ObjectContainer(no_cache=True)

	if Dict['channels']:
		for item in Dict['channels']:
			title 	= unicode(item['name'])
			thumb 	= item.get('thumb', 'na')
			art 	= item.get('art', 'na')
			url 	= item['url']

		# ADD EACH CHANNEL
			oc.add(CreateVideoClipObject(
				url = item['url'],
				title = '► ' + unicode(item['name']),
				thumb = R(item['thumb']),
				art = R(item['art']),
				summary = unicode(item['summary'])
			))

	# ADD KITV STREAM
	oc.add(CreateVideoClipObject(
		url = Dict['kitvURL'],
		title = '► KITV4',
		thumb = R('icon-KITV.png'),
		art = R('art-KITV.jpg'),
		summary = Dict['kitvSCHEDULE']
	))

	# ADD WEATHER/TRAFFIC/INFO BUTTONS
	if Dict['alerts']:
		for itemI in Dict['alerts']:
			if 'WEATHER' in itemI['name']:
				oc.add(CreateVideoClipObject(
					url = unicode(itemI['url']),
					title = '► ' + unicode(itemI['name']),
					thumb = R(itemI['thumb']),
					art = R(itemI['art']),
					summary = unicode(itemI['summary'])
				))
			else:
				oc.add(DirectoryObject(
					key=Callback(showModal, title=unicode(itemI['name']), summary=unicode(itemI['summary'])),
					title = '⁍ ' + unicode(itemI['name']),
					thumb = R(itemI['thumb']),
					art = R(itemI['art']),
					summary = unicode(itemI['summary'])
				))

	# LASTELY ADD REFRESH BUTTON
	oc.add(DirectoryObject(
		key=Callback(MainMenu),
		title='UPDATE CHANNELS', thumb=R('icon-REFRESH.png'), summary=''
		))

	oc.add(PrefsObject(title='Settings'))
	return oc

####################################################################################

@route(PREFIX + '/stream')
def CreateVideoClipObject(url, title, thumb, art, summary,
						  c_audio_codec = None, c_video_codec = None,
						  c_container = None, c_protocol = None,
						  optimized_for_streaming = True,
						  include_container = False, *args, **kwargs):

	vco = VideoClipObject(
		key = Callback(CreateVideoClipObject,
					   url = url, title = title, thumb = thumb, art = art, summary = summary,
					   optimized_for_streaming = True, include_container = True),
		rating_key = url,
		title = title,
		thumb = thumb,
		art = art,
		summary = summary,
		items = [
			MediaObject(
				parts = [
					PartObject(
						key = HTTPLiveStreamURL(url = url)
					)
				],
				optimized_for_streaming = True
			)
		]
	)

	if include_container:
		return ObjectContainer(objects = [vco], no_cache=True)
	else:
		return vco

####################################################################################

@route(PREFIX+'/load_data')
def load_JSON():
	HTTP.ClearCache()
	Dict.Reset()

	# :: GET A RANDOM STRING TO APPEND TO JSON REQUESTS TO FORCE NEW DATA TO BE LOADED
	ID 		  = HTTP.Request('https://plex.tv/pms/:/ip').content
	RNG 	  = HTTP.Request('http://projects.kitsune.work/aTV/HNC/ping.php?ID='+str(ID)).content

	# :: GET STREAM URL FOR [KITV]
	try:
		KITV_DATA = HTTP.Request('http://www.kitv.com/category/305776/live-stream').content
		KITV_DATA = KITV_DATA.splitlines()
		for line in KITV_DATA:
			if 'anvato.net/rest/v2/mcp/video/' in line:
				anvAPI    = line.split('"')
				result    = HTTP.Request(anvAPI[1]).content
				apiResult = result.splitlines()
				# GET FIRST STREAM FROM RESULT IF HD IS FORCED
				for line in apiResult:
					if '.m3u8' in line:
						Dict['kitvURL'] = line
						break
				if '.m3u8' not in Dict['kitvURL']:
					Log("HNC :: FAILED TO GET [KITV] STREAM")
	except:
		Dict['kitvURL'] = 'http://projects.kitsune.work/aTV/HNC/streams/nofeed.mp4'
		Log("HNC :: FAILED TO GET [KITV] STREAM")
	# :: GET [KITV] CHANNEL SCHEDULE
	try:
		kitvSCHEDULE_DATA = HTTP.Request('http://projects.kitsune.work/aTV/HNC/streams/kitv.html').content
		kitvSCHEDULE_DATA = kitvSCHEDULE_DATA.split('#')
		kitvSCHEDULE      = ''
		for line in kitvSCHEDULE_DATA:
			kitvSCHEDULE += line+'\n'
		if kitvSCHEDULE:
			Dict['kitvSCHEDULE'] = kitvSCHEDULE
		else:
			Dict['kitvSCHEDULE'] = 'DAILY'
			Log("HNC :: FAILED TO LOAD [KITV] SCHEDULE")
	except:
		Dict['kitvSCHEDULE'] = 'DAILY'
		Log("HNC :: FAILED TO LOAD [KITV] SCHEDULE")

	# :: LOAD CHANNELS JSON
	try:
		Dict['channels'] = JSON.ObjectFromString(HTTP.Request(CHANNELS+'?v='+RNG, cacheTime = -1).content)
	except:
		Log("HNC :: FAILED TO LOAD [CHANNELS] JSON")

	# :: LOAD ALERTS JSON
	try:
		Dict['alerts']   = JSON.ObjectFromString(HTTP.Request(ALERTS+'?v='+RNG, cacheTime = -1).content)
	except:
		Log("HNC :: FAILED TO LOAD [ALERTS] JSON")

####################################################################################

def returnMain():
	return load_JSON()

####################################################################################

@route(PREFIX+'/modal')
def showModal(title, summary):
	return ObjectContainer(header=title, message=summary)