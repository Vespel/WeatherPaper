# -*- coding: utf-8 -*-

import epd7in5
import Image
import ImageDraw
import ImageFont
import datetime
from bs4 import BeautifulSoup
import urllib2
from ruuvitag_sensor.ruuvitag import RuuviTag



#näytön alustus
EPD_WIDTH = 640
EPD_HEIGHT = 384
epd = epd7in5.EPD()
epd.init()
kuva = Image.new('1', (EPD_WIDTH, EPD_HEIGHT), 1)    # 1: clear the frame
draw = ImageDraw.Draw(kuva)

#muuttujat
viikonpvat="Maanantai","Tiistai","Keskiviikko","Torstai","Perjantai","Lauantai","Sunnuntai"
kuukaudet="null","Tammikuu","Helmikuu","Maaliskuu","Huhtikuu","Toukokuu","Kesäkuu","Heinäkuu","Elokuu","Syyskuu","Lokakuu","Marraskuu","Joulukuu"
tuntinronyt = int(datetime.datetime.now().strftime('%H'))

vrkmax=-100
vrkmin=100
yomin=100

sadevrk=0
sadeyo=0

huomen=0
onetime=0

y=34
vrkh=0
i=0
x=110

#sääkuvake
def kuvake (kuvake):
	if int(kuvake) <= 2:
		return "J"
	elif int(kuvake) == 3:
			return "F"
	elif int(kuvake) == 4:
			return "A"
	elif int(kuvake) == 13:
			return "H"
	elif int(kuvake) == 3:
			return "F"
	else:
		return kuvake

#ruuvitag luku
sensor = RuuviTag('DB:4B:20:6C:87:87')
data = sensor.update()
ruuvitag="%.1f" % round(float(data['temperature']),1)

#nimipäivä datahaku
url="http://www.webcal.fi/cal.php?id=4&format=xml&start_year=current_year&end_year=current_year&tz=Europe%2FHelsinki"
xml=urllib2.urlopen(url)
soap = BeautifulSoup(xml, 'lxml')
nimet=soap.find_all('event')
for nimi in nimet:
    if datetime.datetime.now().strftime('%Y-%m-%d') == nimi.date.text:
		nimip =str(nimi('name'))[7:-8].replace(",","")
		nimip=nimip.split()
		#nimip = u"" + nimip

#Säädatan haku 24h
url="https://www.yr.no/place/Finland/Laponia/Rovaniemi/varsel_time_for_time.xml"
xml=urllib2.urlopen(url)
soap = BeautifulSoup(xml, 'lxml')
ennusteet=soap.find_all('time')
aurinko=soap.find('sun')
a_nousee=datetime.datetime.strptime(aurinko['rise'],"%Y-%m-%dT%H:%M:%S").strftime('%-H:%M')
a_laskee=datetime.datetime.strptime(aurinko['set'],"%Y-%m-%dT%H:%M:%S").strftime('%-H:%M')


#fontit
f_ = ImageFont.truetype('/home/pi/infonaytto/fontit/ClearSans-Regular.ttf', 18)
f_iso = ImageFont.truetype('/home/pi/infonaytto/fontit/unispace.ttf', 44)
f_symbol_p = ImageFont.truetype('/home/pi/infonaytto/fontit/WeatherIcons.ttf', 40)




# lämpötilannyt
draw.text((x, y-40), str(ruuvitag), font=f_iso, fill=0)
draw.text((x + 170, y-30), "Huomenna", font=f_, fill=0)


#Käydään läpi ennusteet tunti tunnilta
for ennuste in ennusteet:
	tuntinro=int(datetime.datetime.strptime(ennuste['from'],"%Y-%m-%dT%H:%M:%S").strftime('%H'))
	pvanro_xml=int(datetime.datetime.strptime(ennuste['from'],"%Y-%m-%dT%H:%M:%S").strftime('%d'))
	pvanro_now=int(datetime.datetime.now().strftime('%d'))
	i=+1
	#lasketaan seuraavan 24h sademäärä ja min max
	if vrkh <24:
		sadevrk+=float(ennuste.precipitation['value'])
		if int(vrkmin) > int(ennuste.temperature['value']):
			vrkmin = int(ennuste.temperature['value'])
		if int(vrkmax) <int(ennuste.temperature['value']):
			vrkmax = int(ennuste.temperature['value'])
		#print tuntinro,vrkmax,vrkmin
		# lasketaan yön min ja sademäärä
		if tuntinro>=23 or tuntinro<=7:
			if int(yomin) > int(ennuste.temperature['value']):
				yomin = ennuste.temperature['value']
				print tuntinro, yomin, sadeyo
			sadeyo += float(ennuste.precipitation['value'])

		vrkh+=1



	#print sadevrk
	if pvanro_now == pvanro_xml:
		x=120
		#yoy = y
	else:
		if huomen==0:
			print yomin
			#NAPPAA KORTINAATIT JA SIT TULOSTUS LOPUKSI

			yoy=y
			yox=x

			#draw.text((x + 25, y+10), "D", font=f_symbol_p, fill=0)
			y=30

		x=280
		huomen=1
		if tuntinro>22:
			break
	if float(ennuste.precipitation['value'])==0.0:
		sade = ""
	else:
		sade=ennuste.precipitation['value']
	if 23>tuntinro>7:
		draw.text((x+30, y), kuvake(ennuste.symbol['number']), font=f_symbol_p, fill=0)
		draw.text((x+2, y),str(tuntinro) , font=f_, fill=0)
		draw.text((x+60, y), str(ennuste.temperature['value'])+" "+str(sade), font=f_, fill=0)
		y += 23



	if tuntinronyt > 10:
		if onetime == 0:
			#print yoy

			#draw.text((x + 25, yoy+22), "Db", font=f_symbol_p, fill=0)
			onetime = 1
yotxt = u"Yö:"+str(yomin)+"'c / "+ str(sadeyo)+"mm"
draw.text((yox + 2, yoy+10), yotxt, font=f_, fill=0)
#********* Piirtely alkaa
#Vasen palkki
draw.rectangle((0, 0,100,20),fill=0)
draw.text((10, 0), kuukaudet[int(datetime.datetime.now().strftime('%-m'))], font=f_, fill=255)
draw.rectangle((0, 20,100,80))
draw.text((19, 20), datetime.datetime.now().strftime('%-d'), font=f_iso, fill=0)
draw.text((9, 60),viikonpvat[datetime.datetime.now().weekday()], font=f_, fill=0)
draw.text((2, 80), "Aurinko", font = f_, fill = 0)
draw.text((7, 100), a_nousee+"-"+a_laskee, font = f_, fill = 0)
draw.text((2, 130), "Min / Max", font = f_, fill = 0)
draw.text((7, 150),str(vrkmin)+"/"+str(vrkmax), font = f_, fill = 0)
draw.text((2, 180), "Sade", font = f_, fill = 0)
draw.text((7, 200),str(sadevrk)+"mm", font = f_, fill = 0)
draw.text((2, 230), "Nimpparit", font = f_, fill = 0)
#nimmparit ja nimet omille riveille
nimiy=250
for nimi in nimip:
	nimi=u""+nimi
	draw.text((7, nimiy),nimi, font=f_, fill=0)
	nimiy+=20

draw.line((450, 0, 450,384), fill=0)
draw.line((270, 0, 270,384), fill=0)
#tallennetaan kuva levylle ja näyttöön
kuva.save("/home/pi/infonaytto/test.jpg")
epd.display_frame(epd.get_frame_buffer(kuva))


