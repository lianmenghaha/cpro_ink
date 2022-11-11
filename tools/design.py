from os import system, listdir, sep
from svgpathtools import svg2paths, wsvg
from tools.segment import *
from tools.conflict import *
from tools.combine import combinePaths
from tools.shift import getDev, shiftPattern
from tools.save import output_conflict, output_unit
import logging
import copy


class ExtractObj:
    def extractObjects(self, resultdir, deRectPaths):
        resultpath = resultdir + sep
        svgs = listdir(resultpath)
        pathno = 0
        for svg in svgs:
            if '.svg' in svg:
                objfile = 'objects.txt'
                thefile = open(resultpath + objfile, 'w')
                paths, attributes = svg2paths(resultpath + svg)
                for path in paths:
                    s = abs(path.area())
                    if pathno == 0:
                        thefile.write('Chip %f\n' % (s))
                    else:
                        thefile.write("chipo%s %f\n" % (pathno, s))
                    pathno += 1
                    lineno = 0
                    for line in path:
                        lineno += 1
                        thefile.write('line%s: %.3f+%.3fi,%.3f+%.3fi\n' % (
                            lineno, line.start.real, line.start.imag, line.end.real, line.end.imag))
                depathno = 0
                for path in deRectPaths:
                    if len(path) == 4:
                        depathno += 1
                        s = abs(path.area())
                        thefile.write("chipd%s %f\n" % (depathno, s))
                        lineno = 0
                        for line in path:
                            lineno += 1
                            thefile.write('line%s: %.3f+%.3fi,%.3f+%.3fi\n' % (
                                lineno, line.start.real, line.start.imag, line.end.real, line.end.imag))
                thefile.close()
                logger = logging.getLogger('__main__')
                logger.info('svg file %s finished conversion.' % (svg))


class cutPolygon:
    def cutSVG(self, svgdir, resultdir, no_merge_factor, lp_factor, deRectPaths):
        svgpath = svgdir + sep
        resultpath = resultdir + sep
        svgs = listdir(svgpath)
        if len(listdir(resultpath)) == 0:
            for svg in svgs:
                if '.svg' in svg:
                    objfile = svg

                    thefile = resultpath + objfile

                    rawpaths, attributes = svg2paths(svgpath + svg)

                    offsetx, offsety = preconfig(rawpaths)
                    # print("offsetx")
                    # print(offsetx)
                    paths, offsetframe = design_preprocess(rawpaths, attributes, offsetx, offsety)
                    # LM:to see if new pattern has been created
                    # print("#paths before design_preprocess")
                    # print(len(rawpaths))
                    # print(rawpaths)
                    # print("#paths after design_preprocess")
                    # print(len(paths))
                    # print("paths after design_preprocess")
                    # print(paths)
                    # LM:rename each pattern
                    nameindexsvgp = 0
                    for path in paths:
                        nameindexsvgp += 1
                        name = 'p' + str(nameindexsvgp)
                        path.name(name)
                    # for debug
                    # print("nameindex")
                    # print(nameindex)
                    # print("name of path")
                    # for path in paths:
                    # print(path.name)

                    # multiply perimeter
                    # change large_factor default=0.02
                    large_factor = 0.02
                    small_factor = 0.005

                    # determine the small and large dimension of the design
                    # offsetframe: chip frame
                    halfgirth = abs(offsetframe[0].length() + offsetframe[1].length())
                    print("offsetframe[0].length()")
                    print(offsetframe[0].length())
                    print("offsetframe[1].length()")
                    print(offsetframe[1].length())
                    large_ratio = large_factor * halfgirth
                    small_ratio = small_factor * halfgirth
                    # LM
                    print("large_ratio")
                    print(large_ratio)
                    print("small_ratio")
                    print(small_ratio)

                    # unitrect: edge of unit rect
                    unitrect = unitdivision(offsetframe)
                    if no_merge_factor != 0:
                        merging_threshold = no_merge_factor
                    else:
                        merging_threshold = small_ratio

                    distinctpathsDict = {}
                    path_no = 0
                    distinctPaths = []
                    no_merge = {}
                    no_absorption = {}

                    # wsvg each path after rectangular_partition to see if this fct creates inside paths
                    fileindex = 0

                    for path in paths:
                        # wsvg(curdistinctpaths, filename='testoutput.svg', openinbrowser=True)
                        # curdistinctpaths: redraw of the design before conflict detection and deviation!h.
                        # create rect with last hline, in order to redraw the pic
                        curdistinctpaths, allcurcutlines = rectangular_partition(path)

                        # wsvg each paths after rectangular_partition
                        # fileindex += 1
                        # repath=curdistinctpaths[:]
                        # repath.insert(0,offsetframe)
                        # llmf=resultpath+str(fileindex)+objfile
                        # wsvg(repath,filename=llmf,openinbrowser=False)
                        # end

                        removecutlines = []
                        for curcutline in allcurcutlines:
                            if large_ratio != 0:
                                if curcutline.length() >= large_ratio:
                                    removecutlines.append(curcutline)
                        curcombinedPaths = []
                        curMicdistinctpaths = []

                        # LM:rename the path in curdistinctpaths
                        # svgpath.name+rect+int
                        nameindexrect = 0
                        for rectpath in curdistinctpaths:
                            nameindexrect += 1  # the name of path begin at 1
                            name = path.name + 'r' + str(nameindexrect)
                            rectpath.name(name)
                        # for debug
                        # print('nameindexrect')
                        # print(nameindexrect)
                        # print('name of rectpath')
                        # for path in curdistinctpaths:
                        #     print(path.name)

                        # LM:test the relation function
                        # for p in curdistinctpaths:
                        # rlts = p.relations(curdistinctpaths)
                        # print(p.name)
                        # print(rlts)

                        for path in curdistinctpaths:
                            curcombinedPaths.append(path)
                            curMicdistinctpaths.append(path)

                        # for debug
                        # print("curcombinedPaths-allpaths")
                        # print(curcombinedPaths)

                        cur_no_merge = {}  # merging conf.->not connected
                        for path1 in curMicdistinctpaths:
                            # LM:key->path1.name
                            cur_no_merge[path1.name] = []
                            for path2 in curMicdistinctpaths:
                                # LM:path1!=path2->path1.name!=path2.name
                                if path1.name != path2.name:
                                    conflict, dis = no_merge_conflict(path1, path2, merging_threshold, in_pattern=1)
                                    if conflict:
                                        # LM:path1->path1.name
                                        cur_no_merge[path1.name].append(path2.name)
                        # for debug
                        # print('cur_no_merge,before')
                        # print(cur_no_merge)

                        # LM:debug add conf
                        # fileindex +=1
                        # print("fileindex")
                        # print(fileindex)
                        # print("curMicdistinctpaths")
                        # print(curMicdistinctpaths)
                        # determine the conflict
                        cur_no_absorption = {}  # laplace conf.->connected paths
                        keepcutlines = []
                        for path1 in curMicdistinctpaths:
                            # LM:path1->path1.name
                            cur_no_absorption[path1.name] = []
                            for path2 in curMicdistinctpaths:
                                if path1.name != path2.name:
                                    conflict, line = lp_conflict(path1, path2, lp_factor)
                                    # LM:addconf
                                    # LM:if really add
                                    # print("hier if really add?")
                                    # addconf = add_lp_conf(path1,path2)
                                    # print("addconf=")
                                    # print(addconf)
                                    # LM:debug
                                    # print("conflict")
                                    # print(conflict)
                                    # print("addconf")
                                    # print(addconf)
                                    # if conflict == False and addconf == True:
                                    # print("add!!!!!!!!!!!")#no such situation

                                    # we need to delet such situation:
                                    # e.g.,p1 have lp with p2 and p2 have lp with p1
                                    # then if p1 must print ealier than p2
                                    if conflict:
                                        # print("conflict!!")
                                        # print(path1.name)
                                        # print(path2.name)
                                        keepcutlines.append(line)
                                        cur_no_absorption[path1.name].append(path2.name)
                        # for debug
                        # print('cur_No_absorption,before')
                        # print(cur_no_absorption)
                        # no Path()

                        # deal with the situation which mentioned above
                        '''
                        for p1 in curMicdistinctpaths:
                            for p2 in curMicdistinctpaths:
                                if p1.name != p2.name:
                                    conflict1,line1=lp_conflict(p1,p2,lp_factor)
                                    conflict2,line2=lp_conflict(p2,p1,lp_factor)
                                    addconf=add_lp_conf(p1,p2)
                                    if conflict1 and conflict2:
                                        if addconf:
                                            #print(cur_no_absorption)
                                            #print('p2 and p1')
                                            #print(p2.name)
                                            #print(p1.name)
                                            if p1.name in cur_no_absorption[p2.name]:
                                                cur_no_absorption[p2.name].remove(p1.name)
                                        else:
                                            if abs(p1.area() < abs(p2.area())):
                                                if p1.name in cur_no_absorption[p2.name]:
                                                    cur_no_absorption[p2.name].remove(p1.name)
                                            else:
                                                if p2.name in cur_no_absorption[p1.name]:
                                                    cur_no_absorption[p1.name].remove(p2.name)
                                        '''
                        # debug
                        # print('cur_No_absorption,after addconf')
                        # print(cur_no_absorption)

                        for cutl in allcurcutlines:
                            if cutl not in keepcutlines:  # keepcutlines contains the lines that must not be removed.
                                if cutl not in removecutlines:  # removecutlines contains the lines that can be removed.
                                    removecutlines.append(cutl)

                        # object combination
                        flag = 1
                        while (flag == 1):
                            # curMicdistinctpaths = curcombinedPaths
                            # LM:only copy the dictionary
                            curMicdistinctpaths = curcombinedPaths[
                                                  :]  # now curcombinedPaths contains all the rectangles
                            flag = 0
                            for path1 in curMicdistinctpaths:
                                for path2 in curMicdistinctpaths:
                                    # LM:name
                                    if path1.name != path2.name:
                                        if path2 in cur_no_merge[path1.name]:
                                            continue
                                        inter, p = two_paths_intersection(path1, path2)
                                        if len(inter) != 0:
                                            for cut in removecutlines:
                                                cutMline = MicroLine(Coordinate(cut.start), Coordinate(cut.end))
                                                interl, p = two_lines_intersection(cutMline, inter[0])
                                                if interl is not None:
                                                    flag = 1
                                                    newPath = combinePaths(path1, path2, inter)
                                                    # LM:give the name to the newPath<--combined from p1,p2
                                                    newname = path1.name + path2.name
                                                    newPath.name(newname)

                                                    deRectPaths.append(path1)
                                                    deRectPaths.append(path2)

                                                    curcombinedPaths.remove(path1)
                                                    curcombinedPaths.remove(path2)
                                                    curcombinedPaths.append(newPath)  # curcombinedPaths contains the Rectangles that have been combined

                                                    # start newPath, path1, path2, cur_no_merge
                                                    update_conflict(cur_no_merge, path1, newPath)
                                                    update_conflict(cur_no_merge, path2, newPath)
                                                    update_conflict(cur_no_absorption, path1, newPath)
                                                    update_conflict(cur_no_absorption, path2, newPath)
                                                    break
                                            if flag == 1:
                                                break
                                if flag == 1:
                                    break
                        # debug
                        # print('cur_no_absorption,after combine')
                        # print(cur_no_absorption)
                        # no Pattern()
                        # print('curcombinedPaths after combination')
                        # for path in curcombinedPaths:
                        #     print(path.name)

                        # for debug
                        # want to see the paths after combination
                        # print("curcombinedPaths-aftercombination")
                        # print(curcombinedPaths)
                        # intersect not mean no nomerge thus removed some lines -> hao xiang hen dui -> testcases1014
                        # -> if combined, means both paths doesnt have conflict with each other? Yes

                        # Cai_Code
                        # temp_no_merge = cur_no_merge
                        # for con in temp_no_merge.items():
                        # for i in con[1]:
                        # x, p = two_paths_intersection(con[0], i)
                        # if len(x) != 0:
                        # for debug
                        # I want to see if this function is used.
                        # print("yesyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy")
                        # del cur_no_merge[con[0]]
                        # break
                        # LM:realize the same function as above
                        # print("cur_no_merge")
                        # print(cur_no_merge)
                        temp_no_merge = dict(cur_no_merge)
                        for con in temp_no_merge.items():
                            # want to find the key-path
                            # for debug
                            # print('con')
                            # print(con)
                            end = False
                            for pathk in curcombinedPaths:
                                if pathk.name == con[0]:
                                    for i in con[1]:
                                        # want to find the value-path
                                        for pathc in curcombinedPaths:
                                            if pathc.name == i:
                                                x, p = two_paths_intersection(pathk, pathc)
                                                if len(x) != 0:
                                                    # for debug
                                                    # print('after len(x)')
                                                    # print(cur_no_merge)
                                                    del cur_no_merge[con[0]]
                                                    end = True
                                                    break
                                        if end:
                                            break
                                    if end:
                                        break

                        # debug
                        # I want to see the pathnames in curcombinedPaths
                        # print("the name of curcombinedPaths after combination")
                        # for path in curcombinedPaths:
                        # print(path.name)

                        # wsvg each paths after obj. combination
                        # fileindex +=1
                        # repath=curcombinedPaths[:]
                        # repath.insert(0,offsetframe)
                        # llmf=resultpath+str(fileindex)+objfile
                        # wsvg(repath,filename=llmf,openinbrowser=False)
                        # end

                        # Overlap induction
                        flag = 1
                        curdevPaths = []
                        for path in curcombinedPaths:
                            curdevPaths.append(path)
                        # LM:identisch before/after
                        # print("#paths before shift")
                        # print(len(curdevPaths))

                        nameindexcur = 0
                        while (flag == 1):
                            flag = 0
                            curcombinedPaths = curdevPaths[:]
                            nameindexcur += 1
                            for path1 in curcombinedPaths:
                                for path2 in curcombinedPaths:
                                    if path1.name != path2.name:
                                        # debug
                                        # print("path1.name")
                                        # print(path1.name)
                                        # print("path2.name")
                                        # print(path2.name)
                                        inter, p = two_paths_intersection(path1, path2)
                                        if len(inter) != 0:
                                            # print("inter[0]")
                                            # print(inter[0])
                                            if inter[0] in path1:
                                                # print("1")
                                                dev = getDev(path2, inter[0])
                                                newPath = shiftPattern(path1, path1.index(inter[0]), dev, 0.02,
                                                                       large_ratio)
                                                # LM:give newPath a name
                                                newname = path1.name + 's' + str(nameindexcur)
                                                newPath.name(newname)

                                                curdevPaths.remove(path1)
                                                curdevPaths.append(newPath)
                                                # start path1, cur_no_merge, newPath
                                                update_conflict(cur_no_merge, path1, newPath)
                                                update_conflict(cur_no_absorption, path1, newPath)
                                                flag = 1
                                            elif inter[0] in path2:
                                                # print("2")
                                                dev = getDev(path1, inter[0])
                                                newPath = shiftPattern(path2, path2.index(inter[0]), dev, 0.02,
                                                                       large_ratio)
                                                # LM:give newPath a name
                                                newname = path2.name + 's' + str(nameindexcur)
                                                newPath.name(newname)

                                                curdevPaths.remove(path2)
                                                curdevPaths.append(newPath)
                                                update_conflict(cur_no_merge, path2, newPath)
                                                update_conflict(cur_no_absorption, path2, newPath)
                                                flag = 1
                                            if flag == 1:
                                                break
                                if flag == 1:
                                    break
                        # debug
                        # print('cur_no_absorption,after curdev')
                        # print(cur_no_absorption)
                        # print("cur_no_merge, after curdev")
                        # print(cur_no_merge)

                        # LM
                        # print("#path after shift")
                        # print(len(curdevPaths))
                        # for path in curdevPaths:
                        #     print(path.name)

                        # wsvg each paths after shift
                        # fileindex += 1
                        # repath=curdevPaths[:]
                        # repath.insert(0,offsetframe)
                        # llmf=resultpath+str(fileindex)+objfile
                        # wsvg(repath,filename=llmf,openinbrowser=False)
                        # end

                        # LM:delet the useless lines inside each path
                        # paths0 = curdevPaths[:]
                        # for p in curdevPaths:
                        # pl1 = p[:]
                        # pl2 = p[:]
                        # for l1 in pl1:
                        # for l2 in pl2:
                        # l1o = l1.order()
                        # l2o = l2.order()
                        # if l1o.direction == 'h':
                        # if l2o.direction == 'h':
                        # if (l1o.start.real<l2o.start.real) and (l1o.end.real>l2o.end.real):
                        # p.remove(l2)

                        # LM:delet the inside path
                        paths1 = curdevPaths[:]
                        paths2 = curdevPaths[:]
                        opt = offsetframe[0].start  # opt is a point you know is NOT enclosed in path
                        cm = copy.deepcopy(cur_no_merge)
                        cab = copy.deepcopy(cur_no_absorption)
                        pts = []
                        for p1 in paths1:
                            for p2 in paths2:
                                if p1.name != p2.name:
                                    # test if p2 in p1

                                    pts = map(attrgetter('start'), p2)
                                    # print("pts_map:")
                                    # print(list(pts))
                                    ptc = 0
                                    ptscnt = 0
                                    for pt in pts:
                                        # print(type(pt))  # <class 'tools.segment.Coordinate'>
                                        ptscnt += 1
                                        if path_encloses_pt(pt, opt, p1):
                                            ptc += 1

                                    # print("len(list(pts))")
                                    # print(len(list(pts)))
                                    # print(ptscnt)

                                    # if ptc == len(list(pts)):
                                    # LM:0202
                                    if ptc == ptscnt:
                                        # print("here")
                                        curdevPaths.remove(p2)
                                        for con in cm.items():
                                            for cmv in con[1]:
                                                if cmv == p2.name:
                                                    cur_no_merge[con[0]].remove(p2.name)
                                            if con[0] == p2.name:
                                                del cur_no_merge[con[0]]
                                        for con in cab.items():
                                            for cabv in con[1]:
                                                if cabv == p2.name:
                                                    cur_no_absorption[con[0]].remove(p2.name)
                                            if con[0] == p2.name:
                                                del cur_no_absorption[con[0]]
                                        # print("remove")
                                else:
                                    continue
                        # LM:delet the useless lines inside each path
                        # paths0 = curdevPaths[:]
                        # for p in curdevPaths:
                        # pl1 = p[:]
                        # pl2 = p[:]
                        # for l1 in pl1:
                        # for l2 in pl2:
                        # l1o = l1.order()
                        # l2o = l2.order()
                        # if l1o.direction == 'h':
                        # if l2o.direction == 'h':
                        # if (l1o.start.real<l2o.start.real) and (l1o.end.real>l2o.end.real):
                        # p.remove(l2)
                        # wsvg each paths after remove
                        # fileindex += 1
                        # repath=curdevPaths[:]
                        # repath.insert(0,offsetframe)
                        # llmf=resultpath+str(fileindex)+objfile
                        # wsvg(repath,filename=llmf,openinbrowser=False)
                        # end

                        # LM:debug add conf
                        fileindex += 1
                        # print("fileindex")
                        # print(fileindex)
                        # print("curdevPaths")
                        # print(curdevPaths)
                        # for p in curdevPaths:
                        # print(p.name)
                        # print(p)

                        for path in curdevPaths:
                            distinctPaths.append(path)
                            # LM:key->path's name
                            distinctpathsDict[path.name] = path_no
                        # LM:deal with lp.conf->not make infeasible
                        # print("curdevPaths")
                        for p in curdevPaths:
                            # print(p.name)
                            # print(p.area())
                            if p.name in cur_no_absorption[p.name]:
                                cur_no_absorption[p.name].remove(p.name)

                        for p1 in curdevPaths:
                            for p2 in curdevPaths:
                                if p1.name != p2.name:
                                    if p1.name in cur_no_absorption[p2.name]:
                                        if p2.name in cur_no_absorption[p1.name]:
                                            addconf = add_lp_conf(p1, p2)
                                            if addconf:
                                                cur_no_absorption[p2.name].remove(p1.name)

                        for p1 in curdevPaths:
                            for p2 in curdevPaths:
                                if p1.name != p2.name:
                                    if p1.name in cur_no_absorption[p2.name]:
                                        if p2.name in cur_no_absorption[p1.name]:
                                            if abs(p1.area()) < abs(p2.area()):
                                                cur_no_absorption[p2.name].remove(p1.name)
                                            else:
                                                cur_no_absorption[p1.name].remove(p2.name)

                        for p1 in curdevPaths:
                            for p2 in curdevPaths:
                                if p1.name != p2.name:
                                    if p2.name in cur_no_absorption[p1.name]:
                                        addconf = add_lp_conf(p1, p2)
                                        if addconf == False:
                                            if abs(p1.area()) > abs(p2.area()):
                                                cur_no_absorption[p1.name].remove(p2.name)

                        # LM:check lp.conf
                        for p1 in curdevPaths:
                            for p2 in curdevPaths:
                                if p1.name in cur_no_absorption[p2.name]:
                                    if p2.name in cur_no_absorption[p1.name]:
                                        print("NOWAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")

                        # LM:addconf final
                        for p1 in curdevPaths:
                            for p2 in curdevPaths:
                                if p1.name != p2.name:
                                    addconf = add_lp_conf(p1, p2)
                                    if addconf:
                                        if p2.name not in cur_no_absorption[p1.name]:
                                            cur_no_absorption[p1.name].append(p2.name)
                                            # print("hier")

                        # Cai_Code
                        # LM:keep original
                        for con in cur_no_merge.items():
                            if con[1] != []:  # con[1] is the list of path's name,which have conflict with key-path
                                no_merge[con[0]] = con[1]
                        for con in cur_no_absorption.items():
                            if con[1] != []:
                                no_absorption[con[0]] = con[1]
                        # debug
                        # print('no_absorption')
                        # print(no_absorption)
                        # print("cur_no_absorption final!!!!")
                        # print(cur_no_absorption)

                        path_no += 1

                    # debug
                    print("conflict has been updated")
                    # LM:
                    for con in no_absorption.items():
                        for pname in con[1]:
                            if pname in list(no_absorption.keys()):
                                if no_absorption[pname] in list(no_absorption.keys()):
                                    print(con)
                                    print(pname)
                                    print(no_absorption[pname])
                                    print(no_absorption[no_absorption[pname]])
                    # print(len(no_absorption))
                    # print("no")

                    # LM:debug:try to find out if there ex. 'inside' pattern
                    # insp=distinctPaths[:]
                    # insp.insert(0,offsetframe)
                    # lmf=resultpath+'_lm'+objfile
                    # wsvg(insp,filename=lmf,openinbrowser=False)
                    # end here

                    distance = {}
                    min_distance = 0
                    # distinctPaths = distinctpathsDict.keys()
                    if len(distinctPaths) >= 2:
                        min_distance = two_paths_distance(distinctPaths[0], distinctPaths[1])
                    length = len(distinctPaths)
                    for p in distinctPaths:
                        # LM:key:p.name
                        distance[p.name] = {}
                    for i in range(0, length):
                        for j in range(i + 1, length):
                            dis = two_paths_distance(distinctPaths[i], distinctPaths[j])
                            if dis > 0 and (dis < min_distance or min_distance <= 0):
                                min_distance = dis
                            if dis != 0:
                                s1 = abs(distinctPaths[i].area())
                                s2 = abs(distinctPaths[j].area())
                                if s1 <= s2:
                                    try:
                                        # LM:key:path's name
                                        distance[distinctPaths[i].name][distinctPaths[j].name] = dis
                                    except KeyError:
                                        print('key error')
                                        print(len(distinctPaths))
                                        print(j)
                                        print(i)
                                else:
                                    # LM:key:path's name
                                    distance[distinctPaths[j].name][distinctPaths[i].name] = dis

                    for k, v in list(distance.items()):
                        if v == {}:
                            del distance[k]

                    # parameter for merging_threshold
                    min_distance = max(0, min_distance)
                    print("min_distance")
                    print(min_distance)

                    if min_distance != 0:
                        min_distance = min(min_distance, small_ratio)
                        merging_threshold = min_distance * 3
                        # LM: New Merging Parameter
                        # merging_threshold = min_distance * 5
                    else:
                        merging_threshold = small_ratio

                    if no_merge_factor != 0:
                        merging_threshold = no_merge_factor

                    no_mergex = {}
                    for p in distinctPaths:
                        # LM:key:p.name
                        no_mergex[p.name] = []
                    for i in range(0, length):
                        for j in range(i + 1, length):
                            dis = 0
                            conflict = None
                            # LM:keys below:path's name
                            if distinctPaths[i].name in list(distance.keys()):
                                if distinctPaths[j].name in distance[distinctPaths[i].name].keys():
                                    dis = distance[distinctPaths[i].name][distinctPaths[j].name]
                            if distinctPaths[j].name in list(distance.keys()):
                                if distinctPaths[i].name in distance[distinctPaths[j].name].keys():
                                    dis = distance[distinctPaths[j].name][distinctPaths[i].name]
                            if distinctpathsDict[distinctPaths[i].name] != distinctpathsDict[distinctPaths[j].name]:
                                conflict, disss = no_merge_conflict(distinctPaths[i], distinctPaths[j],
                                                                    merging_threshold, dis, in_pattern=0)
                            else:
                                conflict, disss = no_merge_conflict(distinctPaths[i], distinctPaths[j],
                                                                    merging_threshold, dis, in_pattern=1)
                            if conflict:
                                no_mergex[distinctPaths[i].name].append(distinctPaths[j].name)
                                no_mergex[distinctPaths[j].name].append(distinctPaths[i].name)
                    for p in distinctPaths:
                        if no_mergex[p.name] == []:
                            del no_mergex[p.name]



                    # LM:in order to configure conflict and decomposition,hide the computation about units.
                    subunits = {}
                    for i in range(0, length):
                        subunits[i + 1] = []
                        subunits[i + 1] = distinctPaths[i].subunit(unitrect, offsetframe)

                    distinctPaths.insert(0, offsetframe)
                    wsvg(distinctPaths, filename=thefile, openinbrowser=False)

                    output_unit(resultpath, 'unit.txt', subunits, unitrect, offsetframe)

                    # hao duo wen ti
                    conflicts = [no_mergex, no_absorption, distance]
                    output_conflict(resultpath, 'conflict.txt', conflicts, distinctPaths)

                    tf = merging_threshold == small_factor
                    logger = logging.getLogger('__main__')
                    logger.info('svg file %s finished partition.' % (svg))
                    logger.info('merging threshold = %s, it %s equals to small_factor' % (merging_threshold, tf))
                    logger.info('absorption threshold = %s' % (lp_factor))
