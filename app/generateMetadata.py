from app.downloadImages import getOutputMetadataFolder, getOutputMetadataPath,addFolder
from app.s3 import upload_with_default_configuration
import os
import json
import gc
from app.settings import BUCKET_NAME 

bucket = BUCKET_NAME

def getPathForS3(orderId, fileName):
    return orderId + "/order/metadata/" + fileName

def startGenerateMetadata(metadata, metadataFormat,orderId):
    
    if(metadataFormat == 'Ethereum'):
        generateJsonMetadata(metadata,orderId)
    elif(metadataFormat == 'Cardano'):
        generateJsonMetadata(metadata,orderId)
    else:
        generateJsonMetadata(metadata,orderId)


def formatMetadataBlock(metadataBlock):
    openSeaFormatMetadata = {
        "name": metadataBlock['NO'],
        "image": "<baseuri>/" + metadataBlock['fileName'],
        "attributes": []
    }
    metadataKeys = filter(lambda x: x != "NO" and x !=
                          "fileName", list(metadataBlock.keys()))
    for key in metadataKeys:
        openSeaFormatMetadata['attributes'].append({
            'trait_type': key,
            'value': metadataBlock[key]
        })
    return openSeaFormatMetadata

def generateJsonMetadata(metadata, orderId):
    for metadataBlock in metadata:
        fileName = metadataBlock['fileName'][:-4] # remove .png for now
        jsonFileName = fileName + ".json"
        outputMetadataFilePath = getOutputMetadataPath(jsonFileName,orderId)
        f = open(outputMetadataFilePath,'w')
        f.write(json.dumps(formatMetadataBlock(metadataBlock)))
        f.close()
          
        upload_with_default_configuration(outputMetadataFilePath,bucket,  getPathForS3(orderId, fileName),os.path.getsize(outputMetadataFilePath) )
        gc.collect()
