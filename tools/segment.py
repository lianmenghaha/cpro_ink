#!/usr/bin/python
import re
from svgpathtools import *
from math import *
from bisect import *
from operator import attrgetter
import numpy as np
from tools.mt import *

import functools

class LineNavigation(object):
    def __init__(self, position, start, end, line):
        self.position = position
        self.start = start
        self.end = end
        self.line = line

    def __repr__(self):
        #return 'Path{} Line{} (start={}, end={}) \n' % (self.pathno, self.lineno, self.start, self.end)
        return '{} {} {}'.format(self.position, self.start, self.end)

    def __cmp__(self, other):
        if hasattr(other, 'position') and hasattr(other, 'start'):
            if(self.position > other.position):
                return 1
            elif(self.position < other.position):
                return -1
            else:
                if (self.start > other.start):
                    return 1
                elif (self.end < other.end):
                    return -1
                else:
                    return 0
# something like key define exist
class Vertex(object):
    def __init__(self, point, hline, vline):
        self.point = point
        self.hline = hline
        self.vline = vline

    def __repr__(self):
        #return 'Path{} Line{} (start={}, end={}) \n' % (self.pathno, self.lineno, self.start, self.end)
        return '{} {} {}'.format(self.point, self.hline, self.vline)

    def __cmp__(self, other):
        e = 0.0000001
        if hasattr(other, 'point'):
            if(self.point.imag - other.point.imag > e):
                return 1
            elif(self.point.imag - other.point.imag < -e ):
                return -1
            else:
                if (self.point.real - other.point.real > e ):
                    return 1
                elif (self.point.real  - other.point.real < -e):
                    return -1
                else:
                    return 0

#LM:0102
#comparing vertex and vertex
def myCmp_Vertex (v1,v2):
    e = 0.0000001
    if hasattr(v2, 'point'):
        if (v1.point.imag - v2.point.imag > e):
            return 1
        elif (v1.point.imag - v2.point.imag < -e):
            return -1
        else:
            if (v1.point.real - v2.point.real > e):
                return 1
            elif (v1.point.real - v2.point.real < -e):
                return -1
            else:
                return 0

class Coordinate(complex):#complex: built-in type

    def __lt__(self, other):
        e = 0.0000001
        if hasattr(other, 'imag') and hasattr(other, 'real'):
            if (self.real - other.real > e):
                return 0
            elif (self.real - other.real < -e):
                return 1
            else:
                if (self.imag - other.imag > e):
                    return 0
                elif (self.imag - other.imag < -e):
                    return 1
                else:
                    return 0
        else:
            return NotImplemented

    def __gt__(self, other):
        e = 0.0000001
        if hasattr(other, 'imag') and hasattr(other, 'real'):
            if (self.real - other.real > e):
                return 1
            elif (self.real - other.real < -e):
                return 0
            else:
                if (self.imag - other.imag > e):
                    return 1
                elif (self.imag - other.imag < -e):
                    return 0
                else:
                    return 0
        else:
            return NotImplemented

    def __le__(self, other):
        e = 0.0000001
        if hasattr(other, 'imag') and hasattr(other, 'real'):
            if (self.real - other.real > e):
                return 0
            elif (self.real - other.real < -e):
                return 1
            else:
                if (self.imag - other.imag > e):
                    return 0
                elif (self.imag - other.imag < -e):
                    return 1
                else:
                    return 1
        else:
            return NotImplemented

    def __ge__(self, other):
        e = 0.0000001
        if hasattr(other, 'imag') and hasattr(other, 'real'):
            if (self.real - other.real > e):
                return 1
            elif (self.real - other.real < -e):
                return 0
            else:
                if (self.imag - other.imag > e):
                    return 1
                elif (self.imag - other.imag < -e):
                    return 0
                else:
                    return 1
        else:
            return NotImplemented

    def __eq__(self, other):
        e = 0.0000001
        if hasattr(other, 'imag') and hasattr(other, 'real'):
            if (abs(self.real - other.real) < e) and (abs(self.imag - other.imag) < e):
                return 1
            else:
                return 0
        else:
            return NotImplemented

class MicroLine(Line):#Line: class in svgpathtools
    #def __eq__(self, other):
	#if isinstance(other, self.__class__):
	    #if super(MicroLine, self).__eq__(other):
		#return True
	    #elif self.end == other.start and self.start == other.end:
		#return True
	    #else:
		#return False
	#else:
	    #return NotImplemented
    #LM:Probe
    def __eq__(self,other):
        if not isinstance(other,MicroLine):
            return NotImplemented
        if self.start == other.start and self.end == other.end:
            return True
        elif self.end == other.start and self.start == other.end:
            return True
        else:
            return False
    #Probe end here.
    #result:no use, no difference.

    @property
    def direction(self):
        if self.start.imag == self.end.imag:#horizontal lines:y bleibt
            return 'h'
        elif self.start.real == self.end.real:#vertical lines:x bleibt
            return 'v'
        else:
            return NotImplemented

    def __cmp__(self, other):
        if hasattr(other, 'start') and hasattr(other, 'end'):
            self = self.order()
            other = other.order()
            # assert if not parallel
            if self.direction == 'h' and other.direction == 'h':
                if (self.start.imag > other.start.imag):
                    return 1
                elif (self.start.imag < other.start.imag):
                    return -1
                else:
                    if (self.start.real > other.start.real):
                        return 1
                    elif (self.end.real < other.end.real):
                        return -1
                    else:
                        return 0
            elif self.direction == 'v' and other.direction == 'v':
                if (self.start.real > other.start.real):
                    return 1
                elif (self.start.real < other.start.real):
                    return -1
                else:
                    if (self.start.imag > other.start.imag):
                        return 1
                    elif (self.end.imag < other.end.imag):
                        return -1
                    else:
                        return 0
            else:
                return 0

    def order(self):
        orderedLine = MicroLine(min(self.start, self.end), max(self.start, self.end))
        return orderedLine
#LM:0102
#Comparsion of MicroLines
def myCmp_MicroLine(m1,m2):
    if hasattr(m2, 'start') and hasattr(m2, 'end'):
        m1 = m1.order()
        m2 = m2.order()
        # assert if not parallel
        if m1.direction == 'h' and m2.direction == 'h':
            if (m1.start.imag > m2.start.imag):
                return 1
            elif (m1.start.imag < m2.start.imag):
                return -1
            else:
                if (m1.start.real > m2.start.real):
                    return 1
                elif (m1.end.real < m2.end.real):
                    return -1
                else:
                    return 0
        elif m1.direction == 'v' and m2.direction == 'v':
            if (m1.start.real > m2.start.real):
                return 1
            elif (m1.start.real < m2.start.real):
                return -1
            else:
                if (m1.start.imag > m2.start.imag):
                    return 1
                elif (m1.end.imag < m2.end.imag):
                    return -1
                else:
                    return 0
        else:
            return 0


# rectlinear pattern
class Pattern(Path):#Path: class in svgpathtools
    #LM:define a function to name pattern
    name='noname'
    def name(self,name):
        self.name=name
    #LM:define a function to determine the relations between self and a list of paths
    #return a dict
    def relations(self,paths):
        rlts={}
        e=0.0000001
        for p in paths:
            if self.name == p.name:
                rlts[self.name]='s'
            else:#not the same path
                dis = two_paths_distance(self,p)
                if dis < e:
                    rlts[p.name]='c'#connected
                else:
                    rlts[p.name]='nc'#not connected
        return rlts

    def preprocess(self):
        """

        :return: filteredPaths - filter path with same start and end points
        """
        hlines = []
        vlines = []
        filteredPath = Pattern()
        filteredVertexObj = []
        filteredVertex = []
        path=[]
        #LM:temporary path: store the original information
        temppath=[]

        #add lines in the path
        #add lines in the temppath
        for line in self:
            start = Coordinate(round(line.start.real, 3), round(line.start.imag, 3))
            end = Coordinate(round(line.end.real, 3), round(line.end.imag, 3))
            newline = MicroLine(start, end)
            temppath.append(line)
            path.append(newline)
        
        #the number of the lines of original path
        lenpath=len(temppath)
        #orthogonalization
        for i in range(0,lenpath):
            #the line we set as standard
            standardsr=round(temppath[i].start.real,3)
            standardsi=round(temppath[i].start.imag,3)
            standarder=round(temppath[i].end.real,3)
            standardei=round(temppath[i].end.imag,3)
            #if it is neither horizontal nor vertical
            #we need to correct 4 elements
            #the error we set as 0.05
            e=0.05
            if standardsr != standarder and standardsi != standardei:
                #print("begin orthogonalization")
                if abs(standardsr-standarder) <= e:#the incorrect coordinate is x
                    corX = round(0.5*(standardsr+standarder),3)
                    #the 1st line is incorrect (not vertical)
                    if i==0:
                        #path[0].start.real=corX
                        #path[0].end.real=corX
                        #path[1].start.real=corX
                        #path[-1].end.real=corX
                        path[-1]=MicroLine(Coordinate(round(temppath[-1].start.real,3),round(temppath[-1].start.imag,3)),Coordinate(corX,standardsi))
                        path[0]=MicroLine(Coordinate(corX,standardsi),Coordinate(corX,standardei))
                        path[1]=MicroLine(Coordinate(corX,standardei),Coordinate(round(temppath[1].end.real,3),round(temppath[1].end.imag,3)))
                    #the last line is incorrect
                    if i==lenpath-1:
                        #path[i-1].end.real=corX
                        #path[i].start.real=corX
                        #path[i].end.real=corX
                        #path[0].start.real=corX
                        path[i-1]=MicroLine(Coordinate(round(temppath[i-1].start.real,3),round(temppath[i-1].start.imag,3)),Coordinate(corX,standardsi))
                        path[i]=MicroLine(Coordinate(corX,standardsi),Coordinate(corX,standardei))
                        path[0]=MicroLine(Coordinate(corX,standardei),Coordinate(round(temppath[0].end.real,3),round(temppath[0].end.imag,3)))
                    #the rest lines
                    else:
                        #path[i-1].end.real=corX
                        #path[i].start.real=corX
                        #path[i].end.real=corX
                        #path[i+1].start.real=corX
                        path[i-1]=MicroLine(Coordinate(round(temppath[i-1].start.real,3),round(temppath[i-1].start.imag,3)),Coordinate(corX,standardsi))
                        path[i]=MicroLine(Coordinate(corX,standardsi),Coordinate(corX,standardei))
                        path[i+1]=MicroLine(Coordinate(corX,standardei),Coordinate(round(temppath[i+1].end.real,3),round(temppath[i+1].end.imag,3)))
                if abs(standardsi-standardei) <= e:#the incorrect coordinate is y
                    corY=round(0.5*(standardsi+standardei),3)
                    #the 1st line is incorrect (not horizontal)
                    if i==0:
                        #path[0].start.imag=corY
                        #path[0].end.imag=corY
                        #path[1].start.imag=corY
                        #path[-1].end.imag=corY
                        path[-1]=MicroLine(Coordinate(round(temppath[-1].start.real,3),round(temppath[-1].start.imag,3)),Coordinate(standardsr,corY))
                        path[0]=MicroLine(Coordinate(standardsr,corY),Coordinate(standarder,corY))
                        path[1]=MicroLine(Coordinate(standarder,corY),Coordinate(round(temppath[1].end.real,3),round(temppath[1].end.imag,3)))
                    #the last line is incorrect
                    if i==lenpath-1:
                        #print(corY)
                        #path[i-1].end.imag=corY
                        #path[i].start.imag=corY
                        #path[i].end.imag=corY
                        #path[0].start.imag=corY
                        path[i-1]=MicroLine(Coordinate(round(temppath[i-1].start.real,3),round(temppath[i-1].start.imag,3)),Coordinate(standardsr,corY))
                        path[i]=MicroLine(Coordinate(standardsr,corY),Coordinate(standarder,corY))
                        path[0]=MicroLine(Coordinate(standarder,corY),Coordinate(round(temppath[0].end.real,3),round(temppath[0].end.imag,3)))
                    else:
                        #path[i-1].end.imag=corY
                        #path[i].start.imag=corY
                        #path[i].end.imag=corY
                        #path[i+1].start.imag=corY
                        path[i-1]=MicroLine(Coordinate(round(temppath[i-1].start.real,3),round(temppath[i-1].start.imag,3)),Coordinate(standardsr,corY))
                        path[i]=MicroLine(Coordinate(standardsr,corY),Coordinate(standarder,corY))
                        path[i+1]=MicroLine(Coordinate(standarder,corY),Coordinate(round(temppath[i+1].end.real,3),round(temppath[i+1].end.imag,3)))
	

	    #add lines in a path: vertical and horizontal list
        for line in path:
            if line.start != line.end:
                if line.direction == 'h':
                    hlines.append(line)
                if line.direction == 'v':
                    vlines.append(line)

        sortedhlines = combineLines(hlines)#self-defined fct,see below
        sortedvlines = combineLines(vlines)
        #print("len(sortedhlines)")
        #print(len(sortedhlines))
        #print("sortedhlines")
        #print(sortedhlines)
        #print("len(sortedvlines)")
        #print(len(sortedvlines))
        #print("sortedvlines")
        #print(sortedvlines)
        filteredVlines = []
        filteredHlines = []

        for vline in sortedvlines:
            intersectpoints = []
            for hline in sortedhlines:
                x = line1_intersect_with_line2(vline, hline)
                if len(x) != 0:
                    intersectpoints.append(x[0][0])
            if len(intersectpoints) >= 2:
                newvline = MicroLine(Coordinate(vline.point(min(intersectpoints))),
                                     Coordinate(vline.point(max(intersectpoints))))
                filteredVlines.append(newvline)
        for hline in sortedhlines:
            intersectpoints = []
            for vline in sortedvlines:
                x = line1_intersect_with_line2(hline, vline)
                if len(x) != 0:
                    intersectpoints.append(x[0][0])
            if len(intersectpoints) >= 2:
                newhline = MicroLine(Coordinate(hline.point(min(intersectpoints))),
                                     Coordinate(hline.point(max(intersectpoints))))
                filteredHlines.append(newhline)

        for line in path:
            if line.start != line.end:
                filteredPath.append(line)

        for line in filteredHlines:
            if line.start not in filteredVertex:
                filteredVertex.append(line.start)
                startPoint = Vertex(line.start, None, None)
                filteredVertexObj.append(startPoint)
            if line.end not in filteredVertex:
                filteredVertex.append(line.end)
                endPoint = Vertex(line.end, None, None)
                filteredVertexObj.append(endPoint)
            for pointobj in filteredVertexObj:
                if pointobj.point == line.start:
                    pointobj.hline = line
                if pointobj.point == line.end:
                    pointobj.hline = line

        for line in filteredVlines:
            if line.start not in filteredVertex:
                filteredVertex.append(line.start)
                startPoint = Vertex(line.start, None, None)
                filteredVertexObj.append(startPoint)
            if line.end not in filteredVertex:
                filteredVertex.append(line.end)
                endPoint = Vertex(line.end, None, None)
                filteredVertexObj.append(endPoint)
            for pointobj in filteredVertexObj:
                if pointobj.point == line.start:
                    pointobj.vline = line
                if pointobj.point == line.end:
                    pointobj.vline = line

        return sortedhlines, sortedvlines, filteredPath, filteredVertexObj

    def subunit(self, unitrect, offsetframe):
        assert self.isclosed()  # This question isn't well-defined otherwise
        num_line = len(self)
        # unit_points = []
        unit_points = {}
        unitrect = float(unitrect)
        if num_line == 4:
            b = self.bbox()
            x0 = int(floor((b[0] - offsetframe.start.real) / float(unitrect) + 1))
            x1 = int(ceil((b[1] - offsetframe.start.real) / float(unitrect) + 1))
            y0 = int(floor((b[2] - offsetframe.start.imag) / float(unitrect) + 1))
            y1 = int(ceil((b[3] - offsetframe.start.imag) / float(unitrect) + 1))
            for x in range(x0, x1):
                for y in range(y0, y1):
                    l = 1.0
                    w = 1.0
                    if x == x0:
                        l = x - (b[0] - offsetframe.start.real) / unitrect
                    elif x == (x1 - 1):
                        l = (b[1] - offsetframe.start.real) / unitrect - (x - 1)
                    if y == y0:
                        w = y - (b[2] - offsetframe.start.imag) / unitrect
                    elif y == (y1 - 1):
                        w = (b[3] - offsetframe.start.imag) / unitrect - (y - 1)
                    if x0 == x1 - 1:
                        l = (b[1] - b[0]) / unitrect
                    if y0 == y1 - 1:
                        w = (b[3] - b[2]) / unitrect
                    per = round(l * w, 6)
                    point = (x, y)
                    unit_points[point] = per
            return unit_points
        elif num_line > 4:
            rectpaths = rectangular_partition(self)[0]
            for p in rectpaths:
                new_points = p.subunit(unitrect, offsetframe)
                for k, v in new_points.items():
                    if k in unit_points.keys():
                        unit_points[k] += new_points[k]
                    else:
                        unit_points[k] = v
            # unit_points = list(set(unit_points))
            return unit_points
        else:
            NotImplemented

def preconfig(paths):
    offsetx = paths[0][0].start.real
    offsety = paths[0][0].start.imag
    for path in paths:
        for line in path:
            if line.start.real < offsetx:
                offsetx = line.start.real
            if line.end.real < offsetx:
                offsetx = line.end.real
            if line.start.imag < offsety:
                offsety = line.start.imag
            if line.end.imag < offsety:
                offsety = line.end.imag
    if offsety >= 0:
        offsety = -10
    else:
        offsety -= 10
    if offsetx >= 0:
        offsetx = -10
    else:
        offsetx -= 10
    return offsetx, offsety

# process based on attributes
# todo: 0906 combine original contacted patterns
#LM:deal with transform="matrix(a,b,c,d,e,f)"
def design_preprocess(paths, attributes, offsetx, offsety):
    length = len(attributes)
    scale = [1] * length
    newPathList = []
    result = []
    for i in range(0, length):
        #if attributes[i].has_key(u'transform'):
        if u'transform' in attributes[i]:
            #str = attributes[0].get(u'transform').encode('utf-8')
            str=attributes[i].get(u'transform').encode('utf-8')#LM: 0->i
            #scale
            if re.search("scale",str):
                scaleconfig = re.findall(r"\d+\.?\d*", str)
                scale[i]=float(scaleconfig[0])
            #LM:scalematrix
            if re.search("matrix",str):
                sm=re.findall(r"\d+\.?\d*",str)
                scale[i]=(float(sm[0]),float(sm[1]),float(sm[2]),float(sm[3]),float(sm[4]),float(sm[5]))#transformation matrix a,b,c,d,e,f
                #if scaleconfig[0] != '0':#LM:0->'0'
                #scale[i] = float(re.findall("\d+\.\d+", scaleconfig[0])[0])
        else:
            scale[i] = 1
    for i in range(0, len(paths)):
        newPath = Pattern()
        for line in paths[i]:
            if isinstance(scale[i],float) or isinstance(scale[i],int):#LM:for scale
                newPath.append(Line(line.start * scale[i], line.end * scale[i]))
            if isinstance(scale[i],tuple) and len(scale[i])==6:#LM:for matrix
#Line((xs,ys),(xe,ye))->Line((axs+cys+e,bxs+dys+f),(axe+cye+e,bxe+dye+f))
                newXs=scale[i][0]*line.start.real+scale[i][2]*line.start.imag+scale[i][4]
                newYs=scale[i][1]*line.start.real+scale[i][3]*line.start.imag+scale[i][5]
                newXe=scale[i][0]*line.end.real+scale[i][2]*line.end.imag+scale[i][4]
                newYe=scale[i][1]*line.end.real+scale[i][3]*line.end.imag+scale[i][5]
                newPath.append(Line(complex(newXs,newYs),complex(newXe,newYe)))
        newPathList.append(newPath)
    #debug
    #print("newPathList")
    #print(newPathList)
    for path in newPathList:
        newPath = Pattern()
        for line in path:
            start = Coordinate(round(line.start.real - offsetx, 3), round(line.start.imag - offsety, 3))
            end = Coordinate(round(line.end.real - offsetx, 3), round(line.end.imag - offsety, 3))
            newline = MicroLine(start, end)
            newPath.append(newline)
        result.append(newPath)
    #for debug
    #print("len(result) in design_preprocess")
    #print(len(result))
    #print("result[0]")
    #print(result[0])
    offsetframe = calculateFrame(result)
    return result, offsetframe

def calculateFrame(paths):
    frame = Pattern()
    fb = paths[0].bbox()
    xmin = fb[0]
    xmax = fb[1]
    ymin = fb[2]
    ymax = fb[3]
    # create the frame of the layout
    for path1 in paths:
        b1 = path1.bbox()
        if len(path1) != 4:
            break
        frame = path1
        for path2 in paths:
            if path1 != path2:
                b2 = path2.bbox()
                if b1[0] <= b2[0] <= b1[1] and b1[0] <= b2[1] <= b1[1] and b1[2] <= b2[2] <= b1[3] and \
                        b1[2] <= b2[3] <= b1[3]:
                    pass
                else:
                    frame = Pattern()
                    break
        if frame != Pattern():
            break
    if frame == Pattern():
        for path in paths:
            b = path.bbox()
            if b[0] < xmin:
                xmin = b[0]
            if b[1] > xmax:
                xmax = b[1]
            if b[2] < ymin:
                ymin = b[2]
            if b[3] > ymax:
                ymax = b[3]
        offset = max(xmax - xmin, ymax - ymin) * 0.05
        frame = Pattern(MicroLine(Coordinate(xmin - offset, ymin - offset),
                               Coordinate(xmax + offset, ymin - offset)),
                     MicroLine(Coordinate(xmax + offset, ymin - offset),
                               Coordinate(xmax + offset, ymax + offset)),
                     MicroLine(Coordinate(xmax + offset, ymax + offset),
                               Coordinate(xmin - offset, ymax + offset)),
                     MicroLine(Coordinate(xmin - offset, ymax + offset),
                               Coordinate(xmin - offset, ymin - offset)))
    if frame in paths:
        paths.remove(frame)

    return frame

#combine parallel lines
def combineLines(microlines):#microlines:list of lines
    result = []
    lines = []
    length = len(microlines)
    orderedLines = []
    for line in microlines:
        newline = line.order()
        orderedLines.append(newline)

    #sortedlines = sorted(orderedLines)
    #LM:0102
    sortedlines = sorted(orderedLines, key=functools.cmp_to_key(myCmp_MicroLine))
    k = 0
    for i in range(0, length):
        if i < k:
            continue
        start = sortedlines[i].start
        end = sortedlines[i].end
        newL = MicroLine(start, end)
        for j in range(i + 1, length):
            bj = sortedlines[j].bbox()
            bi = newL.bbox()
            if line1_is_overlap_with_line2(newL, sortedlines[j]) is True:#line1_is_overlap_with_line2:selfdefined function
                end = Coordinate(max(bi[1], bj[1]), max(bi[3], bj[3]))
                newL = MicroLine(start, end)
            else:
                break
        if sortedlines[i].end != end:
            k = j
            if j == length - 1:
                k = length
        newLine = MicroLine(start, end)
        if newLine not in lines:
            lines.append(newLine)
    last,p = two_lines_intersection(sortedlines[-1], lines[-1])
    if last is not None and last == sortedlines[-1]:
        pass
    elif last is not None and last != sortedlines[-1]:
        newLine = MicroLine(min(last.start, sortedlines[-1].start), max(last.end, sortedlines[-1].end))
        lines.remove(lines[-1])
        lines.append(newLine)
    else:
        lines.append(sortedlines[-1])
    for newLine in lines:
        result.append(newLine)
    return result

def combineLinesWithPoints(allLines, cutPoints):
    result = []
    #sortedhlines = sorted(allLines)
    #LM:0102
    sortedhlines = sorted(allLines, key=functools.cmp_to_key(myCmp_MicroLine))

    #sortedPoints = sorted(cutPoints)
    #LM:0102
    sortedPoints = sorted(cutPoints, key= functools.cmp_to_key(myCmp_Vertex))

    processedLine = []
    remainLines = sortedhlines
    processedLineQueue = []
    for pointobj in sortedPoints:
        for line in remainLines:
            if point_on_line(pointobj.point, line):
                start = line.start
                end = pointobj.point
                if start != end:
                    leftLine = MicroLine(start, end)
                    processedLineQueue.append(leftLine)
                indexofline = remainLines.index(line)
                length = len(remainLines)
                tempLines = []
                for i in range(indexofline, length):
                    if point_on_line(pointobj.point, remainLines[i]):
                        start = pointobj.point
                        end = remainLines[i].end
                        if start != end:
                            newLine = MicroLine(start, end)
                            tempLines.append(newLine)
                    else:
                        tempLines.append(remainLines[i])
                remainLines = tempLines
                break
            else:
                processedLineQueue.append(line)
        if len(processedLineQueue) != 0:
            processedLine = combineLines(processedLineQueue)
        processedLineQueue = []
        for line in processedLine:
            if line not in result:
                result.append(line)
    if len(remainLines) != 0:
        processedLine = combineLines(remainLines)
    for line in processedLine:
        if line not in result:
            result.append(line)
    return result

def point_is_contained_in_path(point, path):
    xmin, xmax, ymin, ymax = path.bbox()
    B = (xmin + 1) + 1j * (ymax + 1)
    AB_line = Path(Line(point, B))
    number_of_intersections1 = len(AB_line.intersect(path))
    if number_of_intersections1 % 2:
        return True
    else:
        return False

def line_in_path(line, path):
    try:
        assert path.isclosed()  # This question isn't well-defined otherwise
    except AssertionError:
        #print("AssertionError")
        #print(path.name)
        #print(path)
        raise
    # find a point that's definitely outside path2
    # assert path1 is line
    mid = Coordinate((line.start.real+line.end.real)/2.0,(line.start.imag+line.end.imag)/2.0)
    if (point_is_contained_in_path(line.start, path) or point_on_path(line.start, path)) and (point_is_contained_in_path(line.end, path) or point_on_path(line.end, path)) and (point_is_contained_in_path(mid, path) or point_on_path(mid, path)):
        return True
    else:
        return False

# overlap of two parallel lines
def line1_is_overlap_with_line2(line1, line2):
    b1 = line1.bbox()
    b2 = line2.bbox()
    if max(b1[0], b2[0]) <= min(b1[1], b2[1]) and b1[2] == b2[2] == b1[3] == b2[3]:
        return True
    elif max(b1[2], b2[2]) <= min(b1[3], b2[3]) and b1[0] == b2[0] == b1[1] == b2[1]:
        return True
    else:
        return False

def cutline(line1, line2):
    # assert self longer than other or ...
    # assert overlapped line
    # assert line1 line2 overlapped
    result = []
    l1 = line1.order()
    l2 = line2.order()
    # start != end should inside init line
    if l1.start < l2.start:
        result.append(MicroLine(l1.start, l2.start))
    if l1.end > l2.end:
        result.append(MicroLine(l2.end, l1.end))
    return result

def createPath(lines):
    hlines = []
    vlines = []
    refinedLines = []
    roundLines = []
    for line in lines:
        start = Coordinate(round(line.start.real, 3), round(line.start.imag, 3))
        end = Coordinate(round(line.end.real, 3), round(line.end.imag, 3))
        newLine = MicroLine(start, end)
        roundLines.append(newLine)
    for line in roundLines:
        b = line.bbox()
        if line.start.real == line.end.real:
            vlines.append(line)
        if line.start.imag == line.end.imag:
            hlines.append(line)
    combinevlines = combineLines(vlines)
    combinehlines = combineLines(hlines)
    for line in combinevlines:
        refinedLines.append(line)
    for line in combinehlines:
        refinedLines.append(line)
    path = Pattern()
    path.append(refinedLines[0])
    length = len(refinedLines)
    used = [0] * length
    used[0] = 1

    for i in range(1, length):
        for j in range(1, length):
            if used[j] == 0:
                if path.start == refinedLines[j].start:
                    newLine = refinedLines[j].reversed()
                    newMLine = MicroLine(newLine.start, newLine.end)
                    path.insert(0, newMLine)
                    used[j] = 1
                    break
                elif path.start == refinedLines[j].end:
                    path.insert(0, refinedLines[j])
                    used[j] = 1
                    break
                elif path.end == refinedLines[j].start:
                    path.append(refinedLines[j])
                    used[j] = 1
                    break
                elif path.end == refinedLines[j].end:
                    newLine = refinedLines[j].reversed()
                    newMLine = MicroLine(newLine.start, newLine.end)
                    path.append(newMLine)
                    used[j] = 1
                    break
    return path

# intersect point
def line1_intersect_with_line2(line1, line2):
    x = None
    if line1 != line2:
        x = line1.intersect(line2)
    if line1.start == line2.start:
        return [(0.0, 0.0)]
    elif line1.start == line2.end:
        return [(0.0, 1.0)]
    elif line1.end == line2.start:
        return [(1.0, 0.0)]
    elif line1.end == line2.end:
        return [(1.0, 1.0)]
    elif x is not None:
        if len(x) != 0:
            a = round(x[0][0],3)
            b = round(x[0][1],3)
            return [(a,b)]
        else:
            return []
    else:
        return []

def two_lines_intersection(line1, line2):
    b1 = line1.bbox()
    b2 = line2.bbox()
    x = line1_intersect_with_line2(line1,line2)
    intersection = None
    intersectp = None
    if line1_is_overlap_with_line2(line1, line2):
        start = Coordinate(max(b1[0], b2[0]), max(b1[2], b2[2]))
        end = Coordinate(min(b1[1], b2[1]), min(b1[3], b2[3]))
        if start != end:
            intersection = MicroLine(start, end)
        else:
            intersectp = Coordinate(start)
    elif len(x) != 0:
        intersectp = line1.point(x[0][0])
    return intersection, intersectp

# intersect = intersect lines on the paths
# intersectpath = intersect path if exists

def two_paths_intersection(path1, path2):
    intersect = []
    intersectpoints = []
    pathlines = []
    for line1 in path1:
        for line2 in path2:
            line1 = MicroLine(Coordinate(line1.start), Coordinate(line1.end))
            line2 = MicroLine(Coordinate(line2.start), Coordinate(line2.end))
            if line1 == line2:
                if line1 not in intersect:
                    intersect.append(line1)
                    pathlines.append(line1)
            else:
                line, interpoint = two_lines_intersection(line1, line2)
                if line is not None:
                    newline = MicroLine(Coordinate(line.start), Coordinate(line.end))
                    if newline not in intersect:
                        intersect.append(newline)
                        pathlines.append(newline)
                if interpoint is not None:
                    if interpoint not in intersectpoints:
                        intersectpoints.append(interpoint)

    for line1 in path1:
        if line_in_path(line1, path2):
            if line1 not in intersect:
                pathlines.append(line1)

    for line2 in path2:
        if line_in_path(line2, path1):
            if line2 not in intersect:
                pathlines.append(line2)

    for l in pathlines:
        if l.start not in intersectpoints:
            intersectpoints.append(l.start)
        if l.end not in intersectpoints:
            intersectpoints.append(l.end)
    x = []
    y = []
    for p in intersectpoints:
        if p.real not in x:
            x.append(p.real)
        if p.imag not in y:
            y.append(p.imag)
    x.sort()
    y.sort()
    if len(x) != 2 or len(y) != 2:
        return intersect, None
    l1 = MicroLine(Coordinate(x[0], y[0]), Coordinate(x[1], y[0]))
    l2 = MicroLine(Coordinate(x[1], y[0]), Coordinate(x[1], y[1]))
    l3 = MicroLine(Coordinate(x[1], y[1]), Coordinate(x[0], y[1]))
    l4 = MicroLine(Coordinate(x[0], y[1]), Coordinate(x[0], y[0]))
    intersectpath = Pattern(l1, l2, l3, l4)
    return intersect, intersectpath

def two_lines_distance(line1, line2):
    if line1.direction == line2.direction == 'h':
        dis = line1.start.imag - line2.start.imag
    elif line1.direction == line2.direction == 'v':
        dis = line1.start.real - line2.start.real
    else:
        return NotImplemented
    return dis

#LM:Note: this is not the real intersectlines,only the parallel lines in the lines
# intersectlines in lines for line
def line_intersectlines(line, lines):
    direct = line.direction
    l1 = line.order()
    intersectlines = []
    for l in lines:
        l2 = l.order()
        if l1 != l2:
            if l2.direction == direct == 'h':
                if l1.start.real <= l2.end.real and l1.end.real >= l2.start.real:
                    intersectlines.append(l2)
            if l2.direction == direct == 'v':
                if l1.start.imag <= l2.end.imag and l1.end.imag >= l2.start.imag:
                    intersectlines.append(l2)
    return intersectlines

# Calculate distance when path length is larger than 4
def two_paths_distancex(path1, path2):
    dis = 0
    points1 = []
    points2 = []
    lines1 = []
    lines2 = []
    points1.append(path1.start)
    points2.append(path2.start)
    inter = path1.intersect(path2)

    # change distance function 0522 start
    """
    intersectL, intersectP = two_paths_intersection(path1, path2)
    if intersectP !=
    """
    if len(inter) != 0:
        return dis

    for l1 in path1:
        points1.append(l1.end)
        l = l1.order()
        lines1.append(l)
    for l2 in path2:
        points2.append(l2.end)
        l = l2.order()
        lines2.append(l)
    for p1 in points1:
        for l2 in lines2:
            if l2.direction == 'h' and l2.start.real < p1.real < l2.end.real:
                tmpdis = abs(l2.start.imag - p1.imag)
            elif l2.direction == 'v' and l2.start.imag < p1.imag < l2.end.imag:
                tmpdis = abs(l2.start.real - p1.real)
            else:
                tmpdis = min(sqrt((l2.start.real-p1.real) ** 2 + (l2.start.imag-p1.imag) ** 2), sqrt((l2.end.real-p1.real) ** 2 + (l2.end.imag-p1.imag) ** 2))
            if tmpdis < dis or dis == 0:
                dis = tmpdis
    for p2 in points2:
        for l1 in lines1:
            if l1.direction == 'h' and l1.start.real < p2.real < l1.end.real:
                tmpdis = abs(l1.start.imag - p2.imag)
            elif l1.direction == 'v' and l1.start.imag < p2.imag < l1.end.imag:
                tmpdis = abs(l1.start.real - p2.real)
            else:
                tmpdis = min(sqrt((l1.start.real-p2.real) ** 2 + (l1.start.imag-p2.imag) ** 2), sqrt((l1.end.real-p2.real) ** 2 + (l1.end.imag-p2.imag) ** 2))
            if tmpdis < dis or dis == 0:
                dis = tmpdis
    return dis

def two_paths_distance(path1, path2):
    dev = 0
    if len(path1) > 4 or len(path2) > 4:
        return two_paths_distancex(path1, path2)
    b1 = path1.bbox()
    b2 = path2.bbox()
    ls,path = two_paths_intersection(path1, path2)
    if len(ls) != 0 or path is not None:
        return 0
    #LM:delect these 4 lines of code.
    #if b1[1] < b2[0] and b1[2] > b2[2]:
    #dev = sqrt((b2[0] - b1[1]) ** 2 + (b2[2] - b1[3]) ** 2)
    #elif b2[1] < b1[0] and b2[3] < b1[2]:
    #dev = sqrt((b2[1] - b1[0]) ** 2 + (b2[3] - b1[2]) ** 2)
    if b1[1]<b2[0] and b1[3]<b2[2]:
        dev = sqrt((b2[0] - b1[1]) ** 2 + (b2[2] - b1[3]) ** 2)
    elif b1[1]<b2[0] and b1[2]>b2[3]:
        dev = sqrt((b2[0] - b1[1]) ** 2 + (b1[2] - b2[3]) ** 2)#writing-style:b2[3]-b1[2]
    elif b1[0]>b2[1] and b1[3]<b2[2]:
        dev = sqrt((b1[0] - b2[1]) ** 2 + (b2[2] - b1[3]) ** 2)#writing-style:b1[3]-b2[2]
    elif b1[0]>b2[1] and b1[2]>b2[3]:
        dev = sqrt((b1[0] - b2[1]) ** 2 + (b1[2] - b2[3]) ** 2)
    elif b1[1] < b2[0]:
        dev = b2[0] - b1[1]
    elif b1[3] < b2[2]:
        dev = b2[2] - b1[3]
    elif b2[1] < b1[0]:
        dev = b1[0] - b2[1]
    elif b2[3] < b1[2]:
        dev = b1[2] - b2[3]
    return dev

def createrect(curdistincthlines):
    curdistinctpaths = []
    #curdistincthlines = sorted(curdistincthlines)
    #LM:0102
    curdistincthlines = sorted(curdistincthlines, key= functools.cmp_to_key(myCmp_MicroLine))

    length = len(curdistincthlines)
    used = length * [0]
    # LM:0102
    curdistincthlinesy = list(map(attrgetter('start.imag'), curdistincthlines))
    for i in range(0, length):
        if used[i] == 0:
            intersectlines = []
            intersectlines_ind = []
            for k in range(i + 1, length):
                if curdistincthlines[k].start.real == curdistincthlines[i].start.real and curdistincthlines[i].end.real == curdistincthlines[k].end.real:
                    intersectlines.append(curdistincthlines[k])
                    intersectlines_ind.append(k)
            # LM:0102
            intersectlinesy = list(map(attrgetter('start.imag'), intersectlines))

            nextstart = bisect(intersectlinesy, curdistincthlinesy[i])
            lens = len(intersectlines)
            if nextstart >= lens:
                continue
            nextend = bisect(intersectlinesy, intersectlinesy[nextstart])
            if nextend > lens:
                continue
            for j in range(nextstart, nextend):
                if used[intersectlines_ind[j]] == 0 and used[i] == 0:
                    if curdistincthlines[i].start.real == intersectlines[j].start.real and \
                            curdistincthlines[
                                i].end.real == \
                            intersectlines[j].end.real:
                        UperLine = curdistincthlines[i]
                        Lowerline = intersectlines[j]
                        newPath = Pattern(UperLine, MicroLine(UperLine.end, Lowerline.end),
                                       MicroLine(Lowerline.end, Lowerline.start),
                                       MicroLine(Lowerline.start, UperLine.start))
                        used[intersectlines_ind[j]] = 1
                        used[i] = 1
                        curdistinctpaths.append(newPath)
    return curdistinctpaths

def unitdivision(frame):
    # calculate area of unit
    # unitdim: approximate unit edge size
    # unitrectedge: unit edge size
    dimension = frame[0].length() * frame[1].length()
    unitdim = sqrt(np.true_divide(dimension, 10000) * 1.1)
    n = num_digit(unitdim)
    unitrectedge = round(unitdim, n+2)
    return unitrectedge

def rectangular_partition(path):
    """
    :param path: one original pattern
    :return: curdistinctpaths, allcurcutlines
    """
    cutvpointobjs = []
    cuthlines = []
    allhlines = []
    allcurcutlines = []
    curdistincthlines = []
    removecutline = []
    sortedhlines, sortedvlines, filteredPath, filteredVertex = path.preprocess()
    for pointobj in filteredVertex:
        cuthline = None
        cutvline = None
        intersecthlines = [x for x in sortedhlines if
                           x.start.real <= pointobj.point.real <= x.end.real]
        intersectvlines = [x for x in sortedvlines if
                           x.start.imag <= pointobj.point.imag <= x.end.imag]
        intersecthlinesy = map(attrgetter('start.imag'), intersecthlines)
        intersectvlinesx = map(attrgetter('start.real'), intersectvlines)
        if pointobj.point == pointobj.hline.start:
            end = pointobj.point
            leftvlineno = bisect_left(list(intersectvlinesx), end.real) - 1
            if len(intersectvlines) > leftvlineno >= 0:
                start = Coordinate(intersectvlines[leftvlineno].start.real, end.imag)
                leftcuthline = MicroLine(start, end)
                if line_in_path(leftcuthline, filteredPath):
                    cuthline = leftcuthline
        else:

            start = pointobj.point
            rightvlineno = bisect_right(list(intersectvlinesx), start.real)
            if 0 < rightvlineno < len(intersectvlines):
                end = Coordinate(intersectvlines[rightvlineno].start.real, start.imag)
                rightcuthline = MicroLine(start, end)
                if line_in_path(rightcuthline, filteredPath):

                    cuthline = rightcuthline
        #for debug
        #print("pointobj in rectangular_partition")
        #print(pointobj)
        if pointobj.point == pointobj.vline.start:

            end = pointobj.point
            uphlineno = bisect_left(list(intersecthlinesy), end.imag) - 1
            if len(intersecthlines) > uphlineno >= 0:
                start = Coordinate(end.real, intersecthlines[uphlineno].start.imag)
                upcutvline = MicroLine(start, end)
                if line_in_path(upcutvline, filteredPath):

                    cutvline = upcutvline
                    cutvpoint = Vertex(start, intersecthlines[uphlineno], None)
        else:

            start = pointobj.point
            downhlineno = bisect_right(list(intersecthlinesy), start.imag)
            if 0 < downhlineno < len(intersecthlines):
                end = Coordinate(start.real, intersecthlines[downhlineno].start.imag)
                downcutvline = MicroLine(start, end)
                if line_in_path(downcutvline, filteredPath):

                    cutvline = downcutvline
                    cutvpoint = Vertex(end, intersecthlines[downhlineno], None)


        cutvlinelength = 0
        cuthlinelength = 0
        curcutline = None
        if cutvline is not None:
            cutvlinelength = cutvline.length()
        if cuthline is not None:
            cuthlinelength = cuthline.length()
        if cutvlinelength != 0 and (cuthlinelength > cutvlinelength or cuthlinelength == 0):
            curcutline = cutvline
            cutvpointobjs.append(cutvpoint)
        elif cuthlinelength != 0 and (cutvlinelength >= cuthlinelength or cutvlinelength == 0):
            curcutline = cuthline
            cuthlines.append(curcutline)
            allhlines.append(curcutline)

        if curcutline is not None:
            allcurcutlines.append(curcutline)

    # allcurcutlines: collection of cutlines
    cline_num = len(allcurcutlines)
    cutcutlines = []
    cutlinevpointobjs = []
    for i in range(0, cline_num):
        for j in range(i + 1, cline_num):
            x = line1_intersect_with_line2(allcurcutlines[i], allcurcutlines[j])
            if len(x) != 0:
                if x != [(0.0, 0.0)] and x != [(0.0, 1.0)] and x != [(1.0, 0.0)] and x != [(1.0, 1.0)]:
                    if allcurcutlines[i].direction == 'h':
                        hcline = allcurcutlines[i]
                        vcline = allcurcutlines[j]
                    else:
                        hcline = allcurcutlines[j]
                        vcline = allcurcutlines[i]
                    intersectp = Coordinate(vcline.start.real, hcline.start.imag)
                    newvpoint = Vertex(intersectp, None, None)
                    cutvpointobjs.append(newvpoint)
                    cutlinevpointobjs.append(newvpoint)
                    for replacehline in [allcurcutlines[i], allcurcutlines[j]]:
                        cutcutlines.append(replacehline)
                else:
                    continue
    # cutcutlines: all intersected cutlines
    # allhlines: all h cutlines
    # cutlinevpointobjs: intersected points of cutlines
    replacehlines = []
    for h in allhlines:
        replacehlines.append(h)
    # if there are intersected cutlines, then combine them
    if len(cutlinevpointobjs):
        replacehlines = combineLinesWithPoints(allhlines, cutlinevpointobjs)
    # replacehlines: combined h cutlines
    for line in sortedhlines:
        allhlines.append(line)
    combinedhlines = combineLinesWithPoints(allhlines, cutvpointobjs)
    for line in combinedhlines:

        curdistincthlines.append(line)

    for line in replacehlines:
        curdistincthlines.append(line)
    # curdistincthlines: combinedhlines +  replacehlines
    # cuthlines: all cuthlines - cutcutlines
    curdistinctpaths = createrect(curdistincthlines)
    return curdistinctpaths, allcurcutlines


def point_on_line(point, line):
    l0 = line.order()
    if l0.start.imag == point.imag:
        if l0.start.real <= point.real <= l0.end.real:
            return True
    elif l0.start.real == point.real:
        if l0.start.imag <= point.imag <= l0.end.imag:
            return True
    else:
        return False

def point_on_path(point, path):
    for line in path:
        if point_on_line(point, line):
            return True
    return False

def line_on_path(line, path):
    for pathline in path:
        if line == pathline:
            return path.index(pathline)
        elif line1_is_overlap_with_line2(line, pathline):
            return path.index(pathline)
    return None



	    









