from flask import Flask, request
from app.generateOrder import startGenerateOrder
from app.generateImages import makeGenerateImages
from flask_cors import CORS
from threading import Thread
import shutil
from zipfile import ZipFile
import requests
from app.downloadImages import downloadAll,getImagesPath, getBaseCombinationsOutputImagesFolder,getBaseCombinationsOutputImagesPath,getOutputImagesFolder, getOrderFolder, addFolder, getOutputMetadataFolder
from app.s3 import upload_with_default_configuration
import os

bucket = '123nft'

app = Flask(__name__)

CORS(app, resources={
      r"/generateOrder/*": {"origins": "https://backend123nft.herokuapp.com"}})

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


# check header for auth
@app.route('/generateOrder', methods=['GET', 'POST'])
def fulfillOrder():
     if request.content_type != 'application/json':

        print('Invalid content-type. Must be application/json.')
        return
     if request.method == 'POST':
        data = request.json
        metadata = data['data']['orderData']['metadata']
    
        totalImages = len(metadata)
    
        thread = Thread(target=batchJobs,
                        args=(data, totalImages))
        thread.start()
        orderId = data['data']['_id']

        return {'id': orderId}


def getAllFilePaths(directory):

    # initializing empty file paths list
    file_paths = []

    # crawling through directory and subdirectories
    for root, directories, files in os.walk(directory):
        for filename in files:
            # join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)

    # returning all file paths
    return file_paths


def remove(path):
    """ param <path> could either be relative or absolute. """
    if os.path.isfile(path) or os.path.islink(path):
        os.remove(path)  # remove the file
    elif os.path.isdir(path):
        shutil.rmtree(path)  # remove dir and all contains
    else:
        raise ValueError("file {} is not a file or dir.".format(path))


def getPathForS3(orderId, fileName):
    return orderId + "/order/" + fileName


def cleanUp(orderId):
    remove(orderId)


def zipFiles(orderId, collectionName):
    # specifying the zip file name
    fileName = getOrderFolder(orderId) + os.sep + collectionName + ".zip"
    filePaths = getAllFilePaths(getOrderFolder(orderId))

    with ZipFile(fileName, 'w') as zip:
       # writing each file one by one
        for file in filePaths:
            zip.write(file)

    return fileName


def zipFilesAndUpload(orderId, collectionName):
    fileName = zipFiles(orderId, collectionName)
    upload_with_default_configuration(fileName, bucket,  getPathForS3(
        orderId, collectionName + ".zip"), os.path.getsize(fileName))


combineBaseImages = makeGenerateImages(getImagesPath, getBaseCombinationsOutputImagesPath, False )

def makeMetadataForTwoLayers(layer1Name,layer2Name, layer1Images,layer2Images):
    metadata =[]
    
    if(len(layer2Name)==0):
        for img1 in layer1Images:

            metadata.append({
                'fileName': layer1Name + '-' + img1[:-4]+'.png',
                layer1Name:img1[:-4],
            })
    
    for img1 in layer1Images:
        for img2 in layer2Images:
            
            metadata.append({
                'fileName': layer1Name + '-' + img1[:-4] + '-' + layer2Name  + '-' + img2[:-4] +'.png',
                layer1Name:img1[:-4],
                layer2Name:img2[:-4],
            })
    return metadata

def createBaseImages(projectStructure, rootName, imageUrlsMap, projectLayersDepth,sortedLayerNames, orderId):
    keysLength = len(sortedLayerNames)
    isEven = keysLength % 2 == 0
    rangeTotal = int(keysLength/2 if isEven else (keysLength/2)-1)
    
    for i in range(0, rangeTotal):
        if(i==rangeTotal and not isEven):
            layer1Name = sortedLayerNames[(2*i) ]
            
            layer1Images = projectStructure[rootName][layer1Name]
    
            metadata = makeMetadataForTwoLayers(layer1Name,"", layer1Images,[])
            filteredImageUrlsMap = { rootName:{ layer1Name:imageUrlsMap[rootName][layer1Name] , }}
            combineBaseImages(metadata,filteredImageUrlsMap, projectLayersDepth,orderId)
        else:
            layer1Name = sortedLayerNames[(2*i) ]
            layer2Name = sortedLayerNames[(2*i)+1]
            
            layer1Images = projectStructure[rootName][layer1Name]
            layer2Images = projectStructure[rootName][layer2Name]
    
            metadata = makeMetadataForTwoLayers(layer1Name,layer2Name, layer1Images,layer2Images)
            filteredImageUrlsMap = { rootName:{ layer1Name:imageUrlsMap[rootName][layer1Name] ,layer2Name:imageUrlsMap[rootName][layer2Name] }}
            combineBaseImages(metadata,filteredImageUrlsMap, projectLayersDepth,orderId)

def batchJobs(data, totalImages):
    orderId = data['data']['_id']
    imageUrlsMap = data['data']['orderData']['imageUrlsMap']
    collectionName = data['data']['orderData']['collectionDetails']['collectionName']
    projectLayersDepth = data['data']['orderData']['projectLayersDepth']
    projectStructure = data['data']['orderData']['projectStructure']
    rootName = list(imageUrlsMap.keys())[0]
    layerNames = imageUrlsMap[rootName].keys()
    
    sortedLayerNames = sorted(
        layerNames, key=lambda layerName: projectLayersDepth[layerName], reverse=True)
    
    if(os.path.exists(orderId)):
        cleanUp(orderId)
        
    
    downloadAll(imageUrlsMap, rootName, layerNames, orderId)


    addFolder(getBaseCombinationsOutputImagesFolder(orderId))
    addFolder(getOutputImagesFolder(orderId))
    addFolder(getOutputMetadataFolder(orderId))
    createBaseImages(projectStructure, rootName, imageUrlsMap, projectLayersDepth, sortedLayerNames,orderId)

    threads = []

    
    for i in range(4):
        startIndex = int(i * (totalImages/4))
        endIndex = int(startIndex + (totalImages/4))
        # We start one thread per url present.
        process = Thread(target=startGenerateOrder,
                         args=(data, startIndex, endIndex))

        process.start()
        threads.append(process)
    # We now pause execution on the main thread by 'joining' all of our started threads.
    # This ensures that each has finished processing the urls.
    for process in threads:
        process.join()
    

    zipFilesAndUpload(orderId, collectionName)

    cleanUp(orderId)

    requests.post('https://backend123nft.herokuapp.com/orderComplete', json={'orderID': orderId})

