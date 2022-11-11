from math import ceil

def output_unit(folder, filename, context, unitrect, offsetframe):
    file = open(folder + filename, 'w')
    num_x = ceil(offsetframe[0].length() / unitrect)
    num_y = ceil(offsetframe[1].length() / unitrect)
    file.write('%d %d %f\n' % (num_x, num_y, unitrect))
    for k, v in context.items():
        index = k
        if len(v) != 0:
            l = len(v)
            file.write('o%s %d' % (index, l))
            for li,per in v.items():
                file.write(' (%d,%d, %f)' % (li[0], li[1], per))
            file.write('\n')
    file.write('FIN\n')
    file.close()

def output_conflict(folder, filename, context, distincthpaths):
    conflictfile = open(folder + filename, 'w')
    conflictfile.write('no merge conflict:\n')
    #LM:make a list of the path's name in disticthpaths
    distincthpathsname=[]
    for p in distincthpaths:
        distincthpathsname.append(p.name)

    #debug
    #print('context[0]')
    #print(context[0])
    for k, v in context[0].items():
        index = distincthpathsname.index(k)
        if len(v) != 0:
            l = len(v)
            conflictfile.write('o%s %d' % (index, l))
            for li in v:
                indexl = distincthpathsname.index(li)
                conflictfile.write(' o%s' % (indexl))
            conflictfile.write('\n')
    conflictfile.write('FIN\n')
    conflictfile.write('\nno absorption conflict:\n')
    #debug
    #print('context[1]')
    #print(context[1])
    for k, v in context[1].items():
        index = distincthpathsname.index(k)
        #LM:we want to find which path is k
        kp = []
        for p in distincthpaths:
            if p.name == k:
                kp.append(p)
                break

        if len(v) != 0:
            stri = []
            for l in v:
                #LM: we want to find with path is l
                lp=[]
                for p in distincthpaths:
                    if p.name == l:
                        lp.append(p)
                        break
                #addconf = add_lp_conf(kp[0],lp[0])    
                if abs(kp[0].area()) < abs(lp[0].area()) or abs(kp[0].area()) >= abs(lp[0].area()):
                    indexl = distincthpathsname.index(l)
                    if indexl not in stri:
                        stri.append('o' + str(indexl))
        if len(stri) != 0:
            l = len(stri)
            conflictfile.write('o%s %d' % (index, l))
            for s in stri:
                conflictfile.write(' %s' % (s))
            conflictfile.write('\n')
    conflictfile.write('FIN\n\n')
    conflictfile.write('distance:\n')
    for k, v in context[2].items():
        index = distincthpathsname.index(k)
        if len(v) != 0:
            for o, d in v.items():
                indexl = distincthpathsname.index(o)
                conflictfile.write('o%s o%s %f\n' % (index, indexl, d))
    conflictfile.write('FIN\n')
    conflictfile.close()
