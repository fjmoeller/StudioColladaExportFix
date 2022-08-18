import sys
import xml.etree.ElementTree as ET
import numpy as np


inputArg1 = sys.argv[1]

with open(inputArg1,'r') as file: 
    text=file.readlines() 

toDelete = []
startLine = 0
onRemove = -1

for index, line in enumerate(text):
    #print("index: "+str(index)+" line: "+line[0:30])
    if startLine == 0:
        if line.__contains__('<geometry id="logo-lego">'): #weg
            startLine = index
            #print("found logo definer: "+str(startLine))
            onRemove = 0
        elif line.__contains__('<instance_geometry url="#logo-lego">'): #weg
            startLine = index-2
            #print("found logo user: "+str(startLine))
            onRemove = 1
        elif line.__contains__('<material id="') and line.__contains__('-logo'): #weg
            startLine = index
            #print("found logo material: "+str(startLine))
            onRemove = 2
        elif line.__contains__('<library_cameras>'):
            startLine = index
            #print("found cameras: "+str(startLine))
            onRemove = 3
        elif line.__contains__('<library_lights>'):
            startLine = index
            #print("found lights: "+str(startLine))
            onRemove = 4
        elif line.__contains__('<library_images>'):
            startLine = index
            #print("found images: "+str(startLine))
            onRemove = 5
        elif line.__contains__('<extra>'):
            startLine = index
            #print("found extra: "+str(startLine))
            onRemove = 6


    else:
        if onRemove == 0 and line.__contains__('</geometry>') :
            toDelete.append([startLine,index])
            #print("found logo definer end: "+str(startLine)+","+str(index))
            startLine = 0
            onRemove = -1
        elif onRemove == 1 and line.__contains__('</node>'):
            toDelete.append([startLine,index])
            #print("found logo user end: "+str(startLine)+","+str(index))
            startLine = 0
            onRemove = -1
        elif onRemove == 2 and line.__contains__('</material>'):
            toDelete.append([startLine,index])
            #print("found logo material end: "+str(startLine)+","+str(index))
            startLine = 0
            onRemove = -1
        elif onRemove == 3 and line.__contains__('</library_cameras>'):
            toDelete.append([startLine,index])
            #print("found camera end: "+str(startLine)+","+str(index))
            startLine = 0
            onRemove = -1
        elif onRemove == 4 and line.__contains__('</library_lights>'):
            toDelete.append([startLine,index])
            #print("found lights end: "+str(startLine)+","+str(index))
            startLine = 0
            onRemove = -1
        elif onRemove == 5 and line.__contains__('</library_images>'):
            toDelete.append([startLine,index])
            #print("found images end: "+str(startLine)+","+str(index))
            startLine = 0
            onRemove = -1
        elif onRemove == 6 and line.__contains__('</extra>'):
            toDelete.append([startLine,index])
            #print("found extra end: "+str(startLine)+","+str(index))
            startLine = 0
            onRemove = -1

#print("toDelete: "+str(toDelete))

with open(inputArg1, 'r') as fr:
    lines = fr.readlines()
    with open(inputArg1, 'w') as fw:
        listcounter = 0
        deleting = False
        for lineindex,line in enumerate(lines):
            #print(lineindex)
            if not deleting:
                if listcounter < len(toDelete) and toDelete[listcounter][0] == lineindex:
                    deleting = True
                else:
                    fw.write(line)
            else:
                if toDelete[listcounter][1] == lineindex:
                    deleting = False
                    #print("Deleted lines:"+str(toDelete[listcounter]))
                    listcounter+=1
    # get the node reference in the visual scene
    # get the node from the node reference
    # get the matrix of the node
    # apply transformations of all subnodes with this matrix




uniqueSubModels = []

namespace='{http://www.collada.org/2005/11/COLLADASchema}'

tree = ET.parse(inputArg1)
root = tree.getroot()

libraryNodes = root.find(namespace+"library_nodes")
rootNodeId = root.find(namespace+"library_visual_scenes")[0][0][1].get("url")[1:]
rootNode = libraryNodes.find("./"+namespace+"node"+"[@id='"+rootNodeId+"']")

rootSubModelNodes = rootNode.findall("./"+namespace+"node"+"["+namespace+"instance_node]")

neutralMatrix = np.matrix("1 0 0 0 0 -1 0 0 0 0 1 0 0 0 0 1", dtype=float).reshape(4,4) #todo put rela here





def printChildren(node):
    for child in node:
        print("child:"+child.tag)
        
def joinMatrix(matrix):
    ret = ""
    for x in np.nditer(matrix):
        ret += " "+str(x)
    
    return ret[1:]
        

def copyDoubleNodes(node):
    print("Copy node: "+str(node.get("id")))
    subModelNodes = node.findall("./"+namespace+"node"+"["+namespace+"instance_node]")
    for subPartNode in subModelNodes:
    
        #printChildren(subPartNode)
        targetNodeUrl = subPartNode.find("./"+namespace+"instance_node").get("url")[1:]
        targetNode = libraryNodes.find("./"+namespace+"node"+"[@id='"+targetNodeUrl+"']")
        
        if targetNodeUrl in uniqueSubModels:
            
            while targetNodeUrl in uniqueSubModels:
                targetNodeUrl+="F"
            
            newNode = ET.fromstring(ET.tostring(targetNode))
            newNode.set("id",targetNodeUrl)
            
            for index, node in enumerate(newNode):
                node.set("id","Inner-"+targetNodeUrl+"-"+str(index))
            
            
            #Find index of targetNode in librarynodes
            index = 0
            for i,node in enumerate(libraryNodes):
                if node==targetNode:
                    index = i
                    break
            
            #TODO insert in the correct order
            libraryNodes.insert(index,newNode)
            
            print("Node copied: "+targetNodeUrl)
            
            subPartNode.find("./"+namespace+"instance_node").set("url","#"+targetNodeUrl)
            
            targetNode = newNode
        
        uniqueSubModels.append(targetNodeUrl)
        
        copyDoubleNodes(targetNode)


#start with rootNode and neutral transformmatrix
def calcNodes(node, transformMatrix):
    #print("------------------------------------------------------------")
    #print("Calc node: "+str(node.get("id")))
    #print("Transformmatrix: "+joinMatrix(transformMatrix))
    partNodes = node.findall("./"+namespace+"node"+"["+namespace+"node]")
    #print("Part nodes found: "+str(len(partNodes)))
    subModelNodes = node.findall("./"+namespace+"node"+"["+namespace+"instance_node]")
    #print("SubModel nodes found: "+str(len(subModelNodes)))

    
    #todo transform matrix of partNodes
    for partNode in partNodes:
        innerNode = partNode.find(namespace+"node")

        innerNodeMatrixNode = innerNode.find("./"+namespace+"matrix")

        #print("partNodeOldMatrix: "+str(innerNodeMatrixNode.text))
        innerNodeMatrix = np.matrix(innerNodeMatrixNode.text, dtype=float).reshape(4,4)
        #print("notTransformedMatrix: "+str(innerNodeMatrix))
        
        nextMatrix=np.matmul(transformMatrix,innerNodeMatrix) # TODO VIELLEICHT EINFACH PLUS????
        #print("partNodeNewMatrix: "+joinMatrix(nextMatrix))
        
        stringdotproduct = joinMatrix(nextMatrix)
        #print("stuff:"+str(stringdotproduct))
        
        innerNodeMatrixNode.text = str(stringdotproduct)
    
    #print("SubMods now--------------------------------")
    
    for subPartNode in subModelNodes:
        subPathMatrixNode = subPartNode.find(namespace+"matrix")

        nextMatrix = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])
        
        if subPathMatrixNode != None:
            subPathMatrix = np.matrix(subPathMatrixNode.text, dtype=float).reshape(4,4)
            #print("notTransformedMatrix: "+str(innerNodeMatrix))
            #print("SubMod old matrix: "+subPathMatrixNode.text)
            
            nextMatrix=np.matmul(transformMatrix,subPathMatrix)
            #print("dotproduct: "+str(dotproduct))
            #print("SubMod new matrix: "+joinMatrix(nextMatrix))
            
            subPartNode.remove(subPathMatrixNode)
            #print("Matrix removed!!")
        

        #printChildren(subPartNode)
        targetNodeUrl = subPartNode.find("./"+namespace+"instance_node").get("url")[1:]
        targetNode = libraryNodes.find("./"+namespace+"node"+"[@id='"+targetNodeUrl+"']")
        
        calcNodes(targetNode, nextMatrix)
    
#print("--------------------------------------------------------------------------------------------------------------")
copyDoubleNodes(rootNode)

#print("--------------------------------------------------------------------------------------------------------------")
calcNodes(rootNode,neutralMatrix)

tree.write(inputArg1)




print("Done")
