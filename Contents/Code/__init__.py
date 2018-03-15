#
	#
		# HAWAII NEWS CHANNELS FOR PLEX
		# VERSION 1.1 | 2017-2018
		# BY OSCAR KAMEOKA FOR THE PEOPLE OF HAWAII ~ WWW.KITSUNE.WORK ~ PROJECTS.KITSUNE.WORK/ATV/
	#
#

import requests


NAME 			= 'HAWAII NEWS'
PREFIX 			= '/video/HawaiiNews'
CHANNELS 		= 'http://projects.kitsune.work/aTV/HNC/channels.json'
ALERTS 			= 'http://projects.kitsune.work/aTV/HNC/alerts.json'

ICON 			= 'icon-default.png'
ART    			= 'art-default.jpg'

kitvSTREAM 		= 'http://projects.kitsune.work/aTV/HNC/streams/nofeed.mp4'
kitvSCHEDULE 	= 'DAILY'

def Start():
	ObjectContainer.title1 	= NAME
	ObjectContainer.art 	= R(ART)
	DirectoryObject.art 	= R(ART)
	VideoClipObject.art 	= R(ART)

	HTTP.CacheTime = 1
	HTTP.ClearCache()

	Dict.Reset()

	load_JSON()

####################################################################################

@handler(PREFIX, NAME, ICON)
def MainMenu():
	global kitvSTREAM, kitvSCHEDULE

	oc = ObjectContainer(no_cache=True)

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
		url = kitvSTREAM,
		title = '► KITV4',
		thumb = R('icon-KITV.png'),
		art = R('art-KITV.jpg'),
		summary = kitvSCHEDULE
	))

	# ADD WEATHER/TRAFFIC/INFO BUTTONS
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
		key=Callback(load_JSON),
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
		#url = url,
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
	global kitvSTREAM, kitvSCHEDULE
	HTTP.ClearCache()

	# STATS TO LET ME THE DEVELOPER KNOW IF I SHOULD KEEP ON INVESTING IN THIS CHANNEL PLUGIN
	ID 		= HTTP.Request('https://plex.tv/pms/:/ip').content
	RNG 	= HTTP.Request('http://projects.kitsune.work/aTV/HNC/ping.php?ID='+str(ID)).content

	# NO-DEPENDENCIES WAY OF GETTING SOURCE WE NEED TO PROCESS M3U8 ADDRESS FOR [KITV]
	page = HTTP.Request('http://www.kitv.com/category/305776/live-stream').content
	page = page.splitlines()
	for line in page:
		if 'anvato.net/rest/v2/mcp/video/' in line:
			anvAPI = line.split('"')
			#if force_HD:
			# FOLLOW API FOR RESPONCE
			result = HTTP.Request(anvAPI[1]).content
			apiResult = result.splitlines()
			# GET FIRST STREAM FROM RESULT IF HD IS FORCED
			for line in apiResult:
				if '.m3u8' in line:
					kitvSTREAM = line
					break
			#else:
			#	kitvSTREAM = anvAPI[1]
	# GET KITV CHANNEL SCHEDULE
	kitvSCHEDULE = ''
	kitvSCHEDULE_DATA = HTTP.Request('http://projects.kitsune.work/aTV/HNC/streams/kitv.html').content
	# FIX LINEBREAKS
	kitvSCHEDULE_DATA = kitvSCHEDULE_DATA.split('#')
	for line in kitvSCHEDULE_DATA:
		kitvSCHEDULE += line+'\n'
	# LOAD CHANNELS JSON
	try:
		dataChannels = JSON.ObjectFromString(HTTP.Request(CHANNELS+'?v='+RNG, cacheTime = 1).content)
	except Exception:
		Log("HNC :: Unable to load [channels] JSON.")
	else:
		Dict['channels'] = dataChannels

	# LOAD ALERTS JSON
	try:
		dataAlerts = JSON.ObjectFromString(HTTP.Request(ALERTS+'?v='+RNG, cacheTime = 1).content)
	except Exception:
		Log("HNC :: Unable to load [alerts] JSON.")
	else:
		Dict['alerts'] = dataAlerts
	return MainMenu()

####################################################################################

def returnMain():
	return load_JSON()

####################################################################################

@route(PREFIX+'/modal')
def showModal(title, summary):
	return ObjectContainer(header=title, message=summary)
