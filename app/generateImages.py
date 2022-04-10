import imageio
import numpy as np
from pathlib import Path
from app.downloadImages import downloadAll, getImagesPath, getOutputImagesPath, addFolder, getOutputImagesFolder
import os
from app.s3 import upload_with_default_configuration

bucket = '123nft'


def getPathForS3(orderId, fileName):
    return orderId + "/order/images/" + fileName


def startGenerateImages(metadata, imageUrlsMap, projectLayersDepth, orderId):
    addFolder(getOutputImagesFolder(orderId))

    rootName = list(imageUrlsMap.keys())[0]
    layerNames = imageUrlsMap[rootName].keys()
    downloadAll(imageUrlsMap, rootName, layerNames, orderId)

    sortedLayerNames = sorted(
        layerNames, key=lambda layerName: projectLayersDepth[layerName], reverse=True)
    for metadataBlock in metadata:
        image = imageio.imread(getImagesPath(
            metadataBlock[sortedLayerNames[0]] + ".png", orderId))
        for layer in sortedLayerNames:
            trait = metadataBlock[layer]
            image = addLayer(getImagesPath(trait + ".png", orderId), image)
        fileName = metadataBlock['fileName']

        saveImg(getOutputImagesPath(fileName, orderId), image)

        outputImagePath = getOutputImagesPath(fileName, orderId)
        upload_with_default_configuration(outputImagePath, bucket,  getPathForS3(
            orderId, fileName), os.path.getsize(outputImagePath))
    return


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
