import sys


inputArg1 = sys.argv[1]

with open(inputArg1,'r') as file: 
    text=file.readlines() 

toDelete = []
startLine = 0

for index, line in enumerate(text):
    print("index: "+str(index)+" line: "+line[0:30])
    if startLine == 0:
        if line.__contains__('<geometry id="logo-lego">'):
            startLine = index
            print("found logo definer: "+str(startLine))
        elif line.__contains__('<instance_geometry url="#logo-lego">'):
            startLine = index-2
            print("found logo user: "+str(startLine))
        elif line.__contains__('<material id="material_id_7-logo"'):
            startLine = index
            print("found logo material: "+str(startLine))
        elif line.__contains__('<library_cameras>'):
            startLine = index
            print("found cameras: "+str(startLine))
        elif line.__contains__('<library_lights>'):
            startLine = index
            print("found lights: "+str(startLine))

    else:
        if line.__contains__('</geometry>'):
            toDelete.append([startLine,index])
            print("found logo definer end: "+str(startLine)+","+str(index))
            startLine = 0
        elif line.__contains__('</node>'):
            toDelete.append([startLine,index])
            print("found logo user end: "+str(startLine)+","+str(index))
            startLine = 0
        elif line.__contains__('</material>'):
            toDelete.append([startLine,index])
            print("found logo material end: "+str(startLine)+","+str(index))
            startLine = 0
        elif line.__contains__('</library_cameras>'):
            toDelete.append([startLine,index])
            print("found camera end: "+str(startLine)+","+str(index))
            startLine = 0
        elif line.__contains__('</library_lights>'):
            toDelete.append([startLine,index])
            print("found lights end: "+str(startLine)+","+str(index))
            startLine = 0

print("toDelete: "+str(toDelete))

with open(inputArg1, 'r') as fr:
    lines = fr.readlines()
    with open(inputArg1, 'w') as fw:
        listcounter = 0
        deleting = False
        for lineindex,line in enumerate(lines):
            print(lineindex)
            if not deleting:
                if listcounter < len(toDelete) and toDelete[listcounter][0] == lineindex:
                    deleting = True
                else:
                    fw.write(line)
            else:
                if toDelete[listcounter][1] == lineindex:
                    deleting = False
                    print("Deleted lines:"+str(toDelete[listcounter]))
                    listcounter+=1
print("Done")





















