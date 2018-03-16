# -*- coding: utf-8 -*-

import epd7in5
import Image
import ImageDraw
import ImageFont
import datetime
from bs4 import BeautifulSoup
import urllib2
#muuttujat

viikonpvat="Ma","Ti","Ke","To","Pe","La","Su"
viikonpvat_p="Maanantai","Tiistai","Keskiviikko","Torstai","Perjantai","Lauantai","Sunnuntai"
ennustex=20
ennustey=320

aikap=datetime.datetime.now().strftime('%d.%-m')
aikak=datetime.datetime.now().strftime('%H:%M')
vkopva_p=datetime.datetime.now().weekday()
print vkopva_p
vkopva_p=viikonpvat_p[vkopva_p]
#näytön alustus
EPD_WIDTH = 640
EPD_HEIGHT = 384
epd = epd7in5.EPD()
epd.init()
image = Image.new('1', (EPD_WIDTH, EPD_HEIGHT), 1)    # 1: clear the frame
draw = ImageDraw.Draw(image)

#nimipäivä
url="http://www.webcal.fi/cal.php?id=4&format=xml&start_year=current_year&end_year=current_year&tz=Europe%2FHelsinki"
xml=urllib2.urlopen(url)
soap = BeautifulSoup(xml, 'lxml')
aikanp=datetime.datetime.now().strftime('%Y-%m-%d')

nimet=soap.find_all('event')

for nimi in nimet:
    #print aikanp
    #print nimi.date.text
    if aikanp == nimi.date.text:
        #s=str(nimi('name')[7:-8])
        #s=s[7:-8]
        nimip = u"Nimipvä: " +str(nimi('name'))[7:-8]

#datan haku
url="https://www.yr.no/place/Finland/Laponia/Rovaniemi/forecast.xml"
xml=urllib2.urlopen(url)
soap = BeautifulSoup(xml, 'lxml')

aurinko=soap.find('sun')
nousee=datetime.datetime.strptime(aurinko['rise'],"%Y-%m-%dT%H:%M:%S").strftime('%H:%M')
laskee=datetime.datetime.strptime(aurinko['set'],"%Y-%m-%dT%H:%M:%S").strftime('%H:%M')
ennusteet=soap.find_all('time')

#fontit
f_vkopva = ImageFont.truetype('/home/pi/infonaytto/fontit/Roboto.ttf', 22)
f_pvm = ImageFont.truetype('/home/pi/infonaytto/fontit/Roboto.ttf', 46)
f_yo = ImageFont.truetype('/home/pi/infonaytto/fontit/Roboto.ttf', 18)
f_paiva = ImageFont.truetype('/home/pi/infonaytto/fontit/Roboto.ttf', 36)
f_symbol = ImageFont.truetype('/home/pi/infonaytto/fontit/WeatherIcons.ttf', 70)
f_symbol_p = ImageFont.truetype('/home/pi/infonaytto/fontit/WeatherIcons.ttf', 40)
f_hipster = ImageFont.truetype('/home/pi/infonaytto/fontit/Hipster.ttf', 110)



#näytölle tulostus
for ennuste in ennusteet:
	if ennuste['period'] == '0':
		yo=ennuste.temperature['value']
		draw.text((ennustex+10, ennustey+40), yo, font = f_yo, fill = 0)
		print(yo)
	
	if ennuste['period'] == '2':
		pvanro=datetime.datetime.strptime(ennuste['from'],"%Y-%m-%dT%H:%M:%S").weekday()
		print(viikonpvat[pvanro])
		draw.text((ennustex+9, ennustey-60), viikonpvat[pvanro], font = f_vkopva, fill = 0)
		#draw.text((ennustex + 10, ennustey - 40), ennuste.symbol['number'], font=f_yo, fill=0)
		if int(ennuste.symbol['number'])<=2:
			draw.text((ennustex, ennustey - 40), "J", font=f_symbol, fill=0)

		elif int(ennuste.symbol['number']) ==3:
			draw.text((ennustex, ennustey - 40), "F", font=f_symbol, fill=0)

		elif int(ennuste.symbol['number']) ==4:
			draw.text((ennustex, ennustey - 40), "A", font=f_symbol, fill=0)
		
		elif int(ennuste.symbol['number']) ==13:
			draw.text((ennustex, ennustey - 40), "H", font=f_symbol, fill=0)

		elif int(ennuste.symbol['number']) >= 5:
			draw.text((ennustex, ennustey - 40), ennuste.symbol['number'], font=f_yo, fill=0)

		paiva=ennuste.temperature['value']
		draw.text((ennustex, ennustey+3), paiva, font = f_paiva, fill = 0)
		print(paiva)
		ennustex +=80


#draw.text((20, 20), "aA bB cC dD", font = f_symbol, fill = 0)

# ruudukko

draw.line((0, 262, 639,262), fill=0)
draw.line((0, 288, 639,288), fill=0)

for x in range(0,641,80):
	draw.line((x, 262, x,640), fill=0)

draw.line((639, 262, 639,640), fill=0)



draw.line((0, 330, 639,330), fill=0)
draw.line((0, 383, 639,383), fill=0)
#draw.rectangle((0, 300, 640, 384), fill = 255)
#draw.rectangle([(2, 2),(100+100) ], outline=(0,0,255,255))
draw.text((1,-4), aikap, font = f_pvm, fill = 0)
draw.text((1,38), vkopva_p, font = f_vkopva, fill = 0)
draw.text((130, 1), nimip, font = f_yo, fill = 0)
draw.text((597, 1),aikak, font = f_yo, fill = 0)
draw.text((121, 21), "J", font=f_symbol_p, fill=0)
draw.text((150, 24), nousee+"-"+laskee, font = f_yo, fill = 0)
draw.text((30,50), "(Pentti on kakka)", font = f_hipster, fill = 0)
draw.text((420,160), "-Peetu", font = f_hipster, fill = 0)

epd.display_frame(epd.get_frame_buffer(image))

image.save("test.jpg")
