import os, sys
import operator
import optparse

#a = QtGui.QApplication([])
if len(sys.argv) != 2:
  print "You must specify an rdfind results text file to process."
  sys.exit(1)

try:
  f = open(sys.argv[1], "r")
except:
  print "Could not open the file: ", sys.argv[1]
  sys.exit(1)
  
  
counts = {}
data = {}
for l in f:
  if l.find("#") == 0:
    continue
  try:
    fid = abs(int(l.split()[1]))
    size = int(l.split()[3])
    name = l.split()[7]

    if not fid in counts:
      counts[fid] = 1
      data[fid] = (size, name)
    else:
      counts[fid] += 1
      data[fid] = (size*counts[fid], size, counts[fid], name, fid)
  except:
    continue
    
b = data.items()
b.sort(key=lambda x:x[1][0])

for i in b:
  print i[1]