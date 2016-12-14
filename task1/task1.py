#!/usr/bin/python
import cv2
# import numpy as np
import sys
import time
import _thread
import os
import subprocess

# http://stream.sunnysubs.com/stream/old3/spz240.m3u8
if len(sys.argv) < 2:
	sys.stderr.write('You must specify name or URL in first argument\n')
	sys.exit(0)


stip_fifo_name = 'stip-fifo.ts'
py_fifo_name = 'py-fifo.ts'
for i in (stip_fifo_name, py_fifo_name):
	if os.path.exists(i):
		os.remove(i)
	os.mkfifo(i)
stip_list_name = 'list.txt'
open(stip_list_name, 'w').write('.'.join(stip_fifo_name.split('.')[:-1]) + '\n')

# patch STIP: 0x0001a57a 488b => eb3a
# and hopefully you have
# libcvaux.so.2  libcv.so.2  libcxcore.so.2  libhighgui.so.2  libml.so.2
# in your ld path or in ./stip-2.0-linux/lib/
env = os.environ.copy()
env['LD_LIBRARY_PATH'] = os.getcwd() + '/stip-2.0-linux/lib'

stip = subprocess.Popen([
	'./stip-2.0-linux/bin/stipdet', '-i', stip_list_name, '-ext', '.' + stip_fifo_name.split('.')[-1],
	'-vpath', './', '-stdout', 'yes', '-o', '/dev/null', '-vis', 'no'
	# ], env=env)
	], stdout=subprocess.PIPE, env=env)

# ffmpeg = subprocess.Popen(
# 	['ffmpeg -i %s -r 5 -s 160x90 -vf format=gray -an -f mpegts - |\
# 	  ffmpeg -y -f mpegts -i - -c copy %s -c copy %s' %
# 		(sys.argv[1], py_fifo_name, stip_fifo_name)
# 	], shell=True, stderr=open(os.devnull, 'w'))

ffmpeg1 = subprocess.Popen(
	['ffmpeg -y -i %s -r 5 -s 160x90 -vf format=gray -an -f mpegts %s' %
		(sys.argv[1], stip_fifo_name)
	], stderr=open(os.devnull, 'w'), shell=True)

ffmpeg2 = subprocess.Popen(
	['ffmpeg -y -i %s -r 5 -s 160x90 -vf format=gray -an -f mpegts %s' %
		(sys.argv[1], py_fifo_name)
	], stderr=open(os.devnull, 'w'), shell=True)

def process_stip():
	while 1:
		# point-type y-norm x-norm t-norm y x t sigma2 tau2 dscr-hog(72) dscr-hof(90)
		tmp = [b'#']
		while tmp[0].startswith(b'#') or tmp == [b'']:
			tmp = stip.stdout.readline().split(b' ')
		point_type = int(tmp[0])
		y_norm = float(tmp[1])
		x_norm = float(tmp[2])
		y = int(tmp[4])
		x = int(tmp[5])
		t = int(tmp[6])
		sigma2 = float(tmp[7])
		tau2 = float(tmp[8])
		hog = list(map(float, tmp[9:9+72]))
		hof = list(map(float, tmp[9+72:9+72+90]))
		print('STIP', t)
		# save this and break some time
	# and apply k-means
	# cv2.kmeans(data, K, criteria, attempts, flags)


def process_ffmpeg():
	cap = cv2.VideoCapture()
	cap.open(py_fifo_name)

	width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
	height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
	fps    = int(cap.get(cv2.CAP_PROP_FPS))
	print('Video Resolution: %d x %d' % (width, height))
	print('Video FPS: %d' % (fps))

	tm = time.time()
	while 1:
		(rv, im) = cap.read()
		if not rv:
			break

		currentFrame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
		print('ffmpeg', currentFrame)

		# if currentFrame % 1000 == 0:
		# 	sys.stderr.write('Going at %.1f fps, done %df\n' % (1000 / (time.time() - tm), currentFrame))
		# 	tm = time.time()

_thread.start_new_thread(process_stip, tuple())
_thread.start_new_thread(process_ffmpeg, tuple())
while 1:
	time.sleep(5)




# cap.release()
# out.release()

# os.remove(stip_fifo_name)
# os.remove(stip_list_name)
