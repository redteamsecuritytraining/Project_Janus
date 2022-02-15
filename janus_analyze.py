#!/user/bin/env python
#
# janus_analyze.py
#

import os
import json
import logging
import requests
import time
from azure.storage.blob import BlobClient

#
# Get Janus config settings from janus_config.json file
# and be sure the json file is in the same folder as this
#
with open('janus_config.json') as json_file:
    config = json.load(json_file)

#
# Log config
#
logfile = config['configuration']['log_file']
logging.basicConfig(filename=logfile, encoding='utf-8', level=logging.INFO)

#
# Make A.I. prediction call with image
#
def getPrediction(filename_with_path):
	# File specific settings
	imagefile = open(filename_with_path).read()
	content_length = os.path.getsize(filename_with_path)

	# Preparing headers for the AI API call
	headers = {"Prediction-Key":str(config['configuration']['prediction_key']), "Content-Type":"application/octet-stream", "Content-Length":str(content_length)}

	# Call AI prediction endpoint and return results
	response = requests.post(config['configuration']['ai_endpoint'], headers=headers, data=imagefile)
	result = json.loads(response.text)
	return result

#
# Loop through results, determine presence
# of key, and upload/notify if key is present
#
def analyzeImage(result, name, filename):
	
	# Counts number of prediction results
	prediction_count = len(result['predictions']) 
	
	# Setting the prediction count to at least 1 
	# result for iteration purposes
	i=1

	# Loop through prediction results
	for x in result['predictions']:
		if (float(x['probability']) > float(config['configuration']['probability_threshold'])):
			print("A key detected in file " + name + " with probability of " + str(x['probability']) + " with threshold at " + str(config['configuration']['probability_threshold']))
			## Log this
			logging.info('<<<<<<< !!! DETECTED a key in image with ' + str(config['configuration']['probability_threshold']) + ' probability:  ' +  filename)
			## Upload key file to Azure Blob Storage
			blob = BlobClient.from_connection_string(conn_str=config['configuration']['connection_string'], container_name=config['configuration']['container_name'], blob_name=name)	
			with open(filename, "rb") as data:
				blob.upload_blob(data)
			# Delete the file per the config setting
			if(config['configuration']['delete_image_after_analysis'] == '1' and prediction_count == i):
				if os.path.exists(filename):
					os.remove(filename)

		else:
			print("Sorry, no key was detected in the file named: " + name + " with probability of " + str(x['probability']) + " with threshold at " + str(config['configuration']['probability_threshold']))
			logging.info('No key found with ' + str(config['configuration']['probability_threshold']) + ' probability in:  ' +  filename)
			# Delete the file per the config setting
			if(config['configuration']['delete_image_after_analysis'] == '1' and prediction_count == i):
				if os.path.exists(filename):
					os.remove(filename)

		# Add 1 to the iteration count
		i=i+1
		continue


###
def main():
	if len(os.listdir(config['configuration']['imagefile_path'])) != 0:
		for filename in os.listdir(config['configuration']['imagefile_path']):
			if filename.endswith(".jpg") or filename.endswith(".jpeg"):
				full_image_path = os.path.join(config['configuration']['imagefile_path'], filename) 
				result = getPrediction(full_image_path)
				analyzeImage(result, filename, full_image_path)
				
			else:
				continue
	print('Image processing done.')

if __name__ == "__main__":
	main()
###