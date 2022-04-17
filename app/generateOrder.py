from app.generateImages import startGenerateImages
from app.generateMetadata import startGenerateMetadata
import os
from zipfile import ZipFile


def startGenerateOrder(request, startIndex, endIndex):
    metadata = request['data']['orderData']['metadata']
    imageUrlsMap = request['data']['orderData']['imageUrlsMap']
    projectLayersDepth = request['data']['orderData']['projectLayersDepth']
    orderId = request['data']['_id']

    metadataFormat = request['data']['orderData']['orderDetails']['metadata']['value']
    
    startGenerateImages(metadata[startIndex:endIndex],
                        imageUrlsMap, projectLayersDepth, orderId)

    startGenerateMetadata(
        metadata[startIndex:endIndex], metadataFormat, orderId)

    return orderId
