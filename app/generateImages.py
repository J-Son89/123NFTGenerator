import imageio
import numpy as np
from pathlib import Path
from app.downloadImages import downloadAll, getImagesPath, getOutputImagesPath, addFolder, getOutputImagesFolder,getBaseCombinationsOutputImagesPath
import os
from app.s3 import upload_with_default_configuration

bucket = '123nft'


def getPathForS3(orderId, fileName):
    return orderId + "/order/images/" + fileName


def addLayer(imageSrc, image):
    img = imageio.imread(imageSrc)
    alpha = img[:, :, 3:] / 255
    layer = img[:, :, :4]
    # Stack new layer onto current image
    return alpha * layer + (1 - alpha) * image


# push to aws
def saveImg(name, image):
    imagePath = (name)
    img_uint8 = image.astype(np.uint8)
    imageio.imwrite(imagePath, img_uint8)


def makeGenerateImages(getImagesPath, getOutputImagesPath, uploadImage):

    def startGenerateImages(metadata, imageUrlsMap, projectLayersDepth, orderId):
    
        rootName = list(imageUrlsMap.keys())[0]
        layerNames = imageUrlsMap[rootName].keys()
    
        sortedLayerNames = sorted(
            layerNames, key=lambda layerName: projectLayersDepth[layerName], reverse=True)
        for metadataBlock in metadata:
            
            image = imageio.imread(getImagesPath(
               sortedLayerNames[0] + '-' + metadataBlock[sortedLayerNames[0]] + ".png", orderId))
            for layer in sortedLayerNames:
                trait = metadataBlock[layer]
                image = addLayer(getImagesPath(layer + '-' + trait + ".png", orderId), image)
            fileName = metadataBlock['fileName']
    
            saveImg(getOutputImagesPath(fileName, orderId), image)
    
            outputImagePath = getOutputImagesPath(fileName, orderId)
            if(uploadImage):
                upload_with_default_configuration(outputImagePath, bucket,  getPathForS3(orderId, fileName), os.path.getsize(outputImagePath))
    return startGenerateImages


def startGenerateImages(metadata, imageUrlsMap, projectLayersDepth, orderId):

    rootName = list(imageUrlsMap.keys())[0]
    layerNames = imageUrlsMap[rootName].keys()

    sortedLayerNames = sorted(
        layerNames, key=lambda layerName: projectLayersDepth[layerName], reverse=True)
    
    keysLength = len(sortedLayerNames)
    isEven = keysLength % 2 == 0
    rangeTotal = int(keysLength/2 if isEven else (keysLength/2))
    
    
    
    for metadataBlock in metadata:
        
        initTrait1 =  sortedLayerNames[0] + '-' + metadataBlock[sortedLayerNames[0]]
        initTrait2 =  sortedLayerNames[1] + '-' + metadataBlock[sortedLayerNames[1]]
        
        image = imageio.imread(getBaseCombinationsOutputImagesPath(
          initTrait1 + '-' + initTrait2 + ".png", orderId))
        
        
        for i in range(2, rangeTotal):
            if( i==rangeTotal and not isEven ):
                layer1Name = sortedLayerNames[(2*i) ]  + '-' + metadataBlock[sortedLayerNames[(2*i)]]
               
                image = addLayer(getBaseCombinationsOutputImagesPath(layer1Name +  ".png", orderId), image)
    
            else:
                layer1Name = sortedLayerNames[(2*i) ]  + '-' + metadataBlock[sortedLayerNames[(2*i)]]
                layer2Name = sortedLayerNames[(2*i)+1] + '-' + metadataBlock[sortedLayerNames[(2*i)+1]]
               
                image = addLayer(getBaseCombinationsOutputImagesPath(layer1Name + '-' + layer2Name + ".png", orderId), image)
            
        
        
        fileName = metadataBlock['fileName']

        saveImg(getOutputImagesPath(fileName, orderId), image)

        outputImagePath = getOutputImagesPath(fileName, orderId)
        upload_with_default_configuration(outputImagePath, bucket,  getPathForS3(orderId, fileName), os.path.getsize(outputImagePath))


