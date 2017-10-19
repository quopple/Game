import os,sys

allFiles=[]
basedir=os.path.join(sys.path[0],"Model/picture")
for parent,dirnames,filenames in os.walk(basedir):
    for filename in filenames:
    	allFiles.append(filename)
#print allFiles

f = open('pictures.txt')
pictures = []
line = f.readline()
while line:
	#print line
	pictures.append(line[0:-1])
	line = f.readline()

#print pictures

f.close()

def isContain(filename):
	try:
		pictures.index(filename)
		return True
	except Exception as e:
		return False

for filename in allFiles:
	if not isContain(filename):
		print 'del',filename
		os.remove(os.path.join(basedir,filename))