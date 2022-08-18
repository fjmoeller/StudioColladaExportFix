import sys
import xml.etree.ElementTree as ET
import numpy as np


inputArg1 = sys.argv[1]


def printChildren(node):
    for child in node:
        print("child:"+child.tag)



#REMOVE STUPID TAGS THAT DESTROY ELEMENTTREE
with open(inputArg1,'r') as file: 
    text=file.readlines() 

toDelete = []
startLine = 0

for index, line in enumerate(text):
    if startLine == 0:
        if line.__contains__('<extra>'):
            startLine = index
    else:
        if line.__contains__('</extra>'):
            toDelete.append([startLine,index])
            startLine = 0

with open(inputArg1, 'r') as fr:
    lines = fr.readlines()
    with open(inputArg1, 'w') as fw:
        listcounter = 0
        deleting = False
        for lineindex,line in enumerate(lines):
            if not deleting:
                if listcounter < len(toDelete) and toDelete[listcounter][0] == lineindex:
                    deleting = True
                else:
                    fw.write(line)
            else:
                if toDelete[listcounter][1] == lineindex:
                    deleting = False
                    listcounter+=1





#PREPARE ELEMENTTREE

namespace='{http://www.collada.org/2005/11/COLLADASchema}'

tree = ET.parse(inputArg1)
root = tree.getroot()


#REMOVE NOT NEEDED STUFF
libraryMaterials = root.find(namespace+"library_materials")
for mat in libraryMaterials:
    if mat.get("id").__contains__("logo"):
        libraryMaterials.remove(mat)

nodes = root.find(namespace+"library_visual_scenes")[0]
nodes.remove(nodes.find("./"+namespace+"node"+"[@id='Camera_Node']"))
nodes.remove(nodes.find("./"+namespace+"node"+"[@id='Light_Node_1']"))
nodes.remove(nodes.find("./"+namespace+"node"+"[@id='Light_Node_2']"))

root.remove(root.find(namespace+"library_cameras"))
root.remove(root.find(namespace+"library_lights"))


#DO THE ACTUAL WORK
uniqueSubModels = []

libraryNodes = root.find(namespace+"library_nodes")

rootNodeId = root.find(namespace+"library_visual_scenes")[0][0][1].get("url")[1:]
startMatrix = np.matrix(root.find(namespace+"library_visual_scenes")[0][0][0].text, dtype=float).reshape(4,4)
rootNode = libraryNodes.find("./"+namespace+"node"+"[@id='"+rootNodeId+"']")


def joinMatrix(matrix):
    ret = ""
    for x in np.nditer(matrix):
        ret += " "+str(x)
    return ret[1:]
    
def copyDoubleNodes(node):
    subModelNodes = node.findall("./"+namespace+"node"+"["+namespace+"instance_node]")
    for subPartNode in subModelNodes:
    
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
            
            libraryNodes.insert(index,newNode)
            
            print("Node copied: "+targetNodeUrl)
            
            subPartNode.find("./"+namespace+"instance_node").set("url","#"+targetNodeUrl)
            
            targetNode = newNode
        
        uniqueSubModels.append(targetNodeUrl)
        
        copyDoubleNodes(targetNode)


#start with rootNode and neutral transform matrix
def calcNodes(node, transformMatrix):
    
    partNodes = node.findall("./"+namespace+"node"+"["+namespace+"node]")
    subModelNodes = node.findall("./"+namespace+"node"+"["+namespace+"instance_node]")
    
    
    #todo transform matrix of partNodes
    for partNode in partNodes:
        innerNode = partNode.find(namespace+"node")

        innerNodeMatrixNode = innerNode.find("./"+namespace+"matrix")

        innerNodeMatrix = np.matrix(innerNodeMatrixNode.text, dtype=float).reshape(4,4)
        
        nextMatrix=np.matmul(transformMatrix,innerNodeMatrix)
        
        stringdotproduct = joinMatrix(nextMatrix)
        
        innerNodeMatrixNode.text = str(stringdotproduct)
    
    for subPartNode in subModelNodes:
        subPathMatrixNode = subPartNode.find(namespace+"matrix")

        nextMatrix = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])
        
        if subPathMatrixNode != None:
            subPathMatrix = np.matrix(subPathMatrixNode.text, dtype=float).reshape(4,4)
            
            nextMatrix=np.matmul(transformMatrix,subPathMatrix)
            
            subPartNode.remove(subPathMatrixNode)
        
        targetNodeUrl = subPartNode.find("./"+namespace+"instance_node").get("url")[1:]
        targetNode = libraryNodes.find("./"+namespace+"node"+"[@id='"+targetNodeUrl+"']")
        
        calcNodes(targetNode, nextMatrix)
    




copyDoubleNodes(rootNode)
calcNodes(rootNode,startMatrix)

tree.write(inputArg1)




print("Done")
