#!/usr/bin/python

 ############################################################################
#                                                                            #
#       Copyright (C) 2009-2010 Thomas Bertani <sylar@anche.no>              #
#                                                                            #
#       This program is free software; you can redistribute it and/or modify #
#       it under the terms of the GNU General Public License as published by #
#       the Free Software Foundation; either version 3 of the License, or    #
#       (at your option) any later version.                                  #
#                                                                            #
#       This program is distributed in the hope that it will be useful,      #
#       but WITHOUT ANY WARRANTY; without even the implied warranty of       #
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the        #
#       GNU General Public License for more details.                         #
#                                                                            #
#       You should have received a copy of the GNU General Public License    #
#       along with this program; if not, write to the Free Software          #
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,           #
#       MA 02110-1301, USA.                                                  #
#                                                                            #
 ############################################################################

import time
t_=time.time()
import os, pygame, string, struct
from time import sleep
from random import randint
from math import *
from sys import argv

def update(screen, mouse_pos, clean = False, show_title = True):
	global state, locket, set_mode
	def check_position_relevant(mouse_pos):
		global circles, status
		inc=44
		c=1
		for i in circles:
			if i[0]-inc<mouse_pos[0]<i[0]+inc and i[1]-inc<mouse_pos[1]<i[1]+inc: break
			c+=1
		if c!=10:
			c-=1
			tn=0
			for n in status:
				if n==c: break
				tn+=1
			if tn==len(status):
				status.append(c)
	def redraw_old(screen):
		global circles, status
		if len(status)<2: return
		n=0
		for i in status[:len(status)-1]:
			pygame.draw.line(screen,(255,255,255),(circles[status[n]]),(circles[status[n+1]]),10)
			n+=1
	def draw_circles(screen):
		global circles, status, img_base, img_selected, font
		c=0
		for i in circles:
			try:
				if status.index(c)!="":
					screen.blit(img_selected,(i[0]-44, i[1]-44))
			except ValueError:
				screen.blit(img_base,(i[0]-44, i[1]-44))
			c+=1
	if clean==False: check_position_relevant(mouse_pos)
	screen.fill((0,0,0))
	pygame.draw.line(screen,(255,255,255),(15,130),(SCREEN_SIZE[0]-15,130),3)
	pygame.draw.line(screen,(255,255,255),(15,SCREEN_SIZE[1]-50),(SCREEN_SIZE[0]-15,SCREEN_SIZE[1]-50),3)
	if not set_mode:
		screen.blit(locket, (40,15))
	else:
		screen.blit(locket, (10,15))
	if show_title==True:
		if not set_mode:
			screen.blit(font.render("Enter your pattern",True,(255,255,255)),(120,60))
		else:
			if step==1:
				screen.blit(font.render("[1/3] Enter the old pattern",True,(255,255,255)),(90,60))
			elif step==2:
				screen.blit(font.render("[2/3] Enter the new pattern",True,(255,255,255)),(90,60))
			elif step==3:
				screen.blit(font.render("[3/3] Re-enter the new pattern",True,(255,255,255)),(90,60))
	redraw_old(screen)
	if clean==False and state=="down" and len(status)!=0:
		pygame.draw.line(screen,(255,255,255),(circles[status[len(status)-1:][0]]),mouse_pos, 10)
	draw_circles(screen)
	pygame.display.update()
def check_status(screen):
		global circles, status, status_ok_, img_wrong, img_right, hidden, ten, set_mode, step, new_pattern_status, no_conf
		if set_mode and step==2:
			step=3
			new_pattern_status=status
			sleep(2)
			return
		elif set_mode and step==3:
			status_ok_=new_pattern_status
		if status==status_ok_:
			c=0
			for i in status:
				screen.blit(img_right, (circles[status[c]][0]-44,circles[status[c]][1]-44))
				c+=1
			if not set_mode:
				screen.blit(font.render("Unlocked!",True,(61,241,49)),(120,60))
			else:
				screen.blit(font.render("Ok!",True,(61,241,49)),(90,60))
			pygame.display.update()
			sleep(1)
			ten=0
			if not set_mode:
				pygame.display.quit()
				hidden=True
			else:
				step+=1
		else:
			if set_mode and step==3:
				screen.blit(font.render("Pattern mismatch!",True,(49,49,241)),(90,60))
				pygame.display.update()
				step=2
				return
			ten+=1
			c=0
			for i in status:
				screen.blit(img_wrong, (circles[status[c]][0]-44, circles[status[c]][1]-44))
				c+=1
			if ten==1:
				ten=2
			stw=0
			for l in range(1,ten):
				stw+=ten**2
			if not set_mode:
				screen.blit(font.render("Wrong pattern!",True,(49,49,241)),(120,60))
			else:
				screen.blit(font.render("Wrong pattern!",True,(49,49,241)),(90,60))
			pygame.display.update()
			for n in range(stw, 0, -1):
				screen.fill((0,0,0))
				if n<60:
					to_wait=str(n)+" seconds"
				else:
					seconds=str(n%60)
					if len(seconds)<2: seconds="0"+seconds
					to_wait=str(n/60)+":"+seconds+" min"
				if not set_mode:
					screen.blit(font.render("You have to wait "+to_wait,True,(49,49,241)),(60,SCREEN_SIZE[1]-40))
					pygame.display.update(pygame.rect.Rect((15,SCREEN_SIZE[1]-40),(SCREEN_SIZE[0]-30,40)))
				if set_mode and step==1:
					screen.blit(font.render("You have to wait "+to_wait,True,(49,49,241)),(90,10))
					pygame.display.update(pygame.rect.Rect((90,10),(SCREEN_SIZE[0],30)))
				sleep(1)
			pygame.display.update()
			status=[]
		if set_mode and step>3:
			print "Saving the new pattern to the configuration file"
			new_pattern_=""
			for i in status:
				new_pattern_+=str(i)
			f=open(os.getenv("HOME")+"/.sl.conf","w")
			f.write(new_pattern_+"\n")
			f.close()
			if not no_conf:
				pygame.quit()
				exit()
def wait_for_aux():
	print "\nWaiting for aux..."
	button = "/dev/input/event0"
	fmt = 'iihhi'
	try:
		in_file = open(button,"rb")
	except:
		return
	event = in_file.read(16)
	while event:
        	(time1,time2, type, code, value) = \
                	struct.unpack(fmt,event)
        	if type == 1 & code == 169 & value == 1:
			in_file.close()		
			return
        	event = in_file.read(16)
	in_file.close()
def load_conf():
	global status_ok_, step, set_mode, no_conf
	status_ok_=[]
	config=os.getenv("HOME")+"/.sl.conf"
	try:
		#print "Loading configuration file (",config,")..."
		f=open(config,"r")
		pattern=f.readline()
		f.close()
		for i in pattern:
			try:
				status_ok_.append(int(i))
			except:
				pass
		if step==0: step=1
		no_conf=False
	except:
		print "Cannot load the configuration file (",config,")"
		if step==1: step=2
		no_conf=True
	#print "patten -> ",status_ok_
status_ok_=[]
set_mode_required=False
step=0
set_mode=False
pygame.init()
print "Time needed to import all modules and to init pygame: ",(time.time()-t_)
t_=time.time()
SCREEN_SIZE = (480,600)
font = pygame.font.SysFont("arial",40)
circles=[(80, 200), (240, 200), (400, 200), (80, 360), (240, 360), (400, 360), (80, 520), (240, 520), (400, 520)]
status=[]
no_conf=False
load_conf()
res = 'res/'
img_base=pygame.image.load(res+'base.bmp')
img_selected=pygame.image.load(res+'selected.bmp')
img_right=pygame.image.load(res+'right.bmp')
img_wrong=pygame.image.load(res+'wrong.bmp')
locket=pygame.image.load(res+'locket.bmp')
state="up"
hidden=True
ten=0
print "Time needed to load resources: ",(time.time()-t_)
t_f=time.time()
updated_once=False
if no_conf:
	set_mode_required=True
try:
	if argv[1]=="--set":
		set_mode_required=True
except:
	pass
if set_mode_required:
	print "entering set_mode!"
	hidden=False
	set_mode=True
	load_conf()
	new_pattern_status=[]
	screen = pygame.display.set_mode(SCREEN_SIZE,0,32)
	pygame.display.set_caption("Screenlocker")
	pygame.mouse.set_visible(False)
	updated_once=False
while 1:
	if hidden:
		wait_for_aux()
		print "aux button pressed!"
		load_conf()
		screen = pygame.display.set_mode(SCREEN_SIZE,0,32)
		pygame.display.set_caption("Screenlocker")
		pygame.display.toggle_fullscreen()
		pygame.mouse.set_visible(False)
		hidden=False
		updated_once=False
	if not hidden and state=="up" and updated_once==False:
		update(screen, pygame.mouse.get_pos(), True)
		updated_once=True
	if not hidden:
		load_conf()
		if state=="up":
			tmp=pygame.event.wait()
			if set_mode and string.find(str(tmp), "12-Quit {}")!=-1:
				print "quit request event received!" 
				pygame.quit()
				exit()
			if string.find(str(tmp), "MouseButtonDown")!=-1:
				print "down (got up from wait event mode)"
				state="down"
			if string.find(str(tmp), "KeyUp {'scancode': 124,")!=-1:
				print "power key pressed!\nsuspending..."
				os.system("apm --suspend")
		else:
			tmp=pygame.event.get()#tmp=pygame.event.get((5,6))
	if not hidden:
		i=tmp
		if i==tmp:
			#print str(i)
			if set_mode and string.find(str(tmp), "12-Quit {}")!=-1:
				print "quit request event received!" 
				pygame.quit()
				exit()
			if string.find(str(i), "MouseButtonDown")!=-1:
				state="down"
				print "down!"
			if string.find(str(i), "MouseButtonUp")!=-1:
				state="up"
				print "up!"
				if len(status)>1:
					update(screen, pygame.mouse.get_pos(), True, False)
					check_status(screen)
				status=[]
				updated_once=False
		if not hidden and state=="down":
			if len(status)==9:
				state="up"
				update(screen, pygame.mouse.get_pos(), True, False)
				check_status(screen)
				status=[]
			elif state=="down":
				update(screen, pygame.mouse.get_pos())
			else:
				update(screen, pygame.mouse.get_pos(), True)
