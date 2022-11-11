from tools.segment import *

def shiftPattern(path, index, dev, factor, large_ratio):
    newPath = Pattern()
    l0 = path[index]
    #debug
    #print(dev)

    if abs(dev * factor) < 0.01*large_ratio:
        #modify parameter (default 0.7)
        devx = dev * factor *20
    elif abs(dev * factor)< large_ratio:
        devx = dev * factor *5
    else:
        devx = dev * factor


    if l0.direction == 'h':
        deviation = Coordinate(0, -devx)
    else:
        deviation = Coordinate(-devx, 0)
    
    #LM
    a=l0.start
    b=l0.end
    da=Coordinate(a+deviation)
    db=Coordinate(b+deviation)
    for line in path:
        '''
        if line != l0:
            point = line1_intersect_with_line2(line, l0)
            if len(point) != 0:
                roundpoint = round(point[0][0], 3)
                if roundpoint == 1:
                    end = Coordinate(line.end + deviation)
                    newPath.append(MicroLine(line.start, end))
                if roundpoint == 0:
                    start = Coordinate(line.start + deviation)
                    newPath.append(MicroLine(start, line.end))
            else:
                newPath.append(line)
        else:
            newLine = MicroLine(Coordinate(l0.start + deviation), Coordinate(l0.end + deviation))
            newPath.append(newLine)
        '''
        start = line.start
        end = line.end
        if line.start == a:
            start = da
        if line.start == b:
            start = db
        if line.end == a:
            end = da
        if line.end == b:
            end = db
        newPath.append(MicroLine(start,end))
    return newPath

def getDev(path, line):
    l0 = line.order()
    intersectlines = line_intersectlines(l0, path)
    dev = two_lines_distance(l0, intersectlines[0])
    for pl in intersectlines:
        if dev == 0:
            dev = two_lines_distance(l0, pl)
            continue
        dis = two_lines_distance(l0, pl)
        if abs(dis) < abs(dev) and dis != 0:
            dev = dis
    return dev

