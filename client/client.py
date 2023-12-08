# 
# Client-side python app for AI Image Detection app, which is calling
# a set of lambda functions in AWS through API Gateway.
# The overall purpose of the app is to process an image and
# calculate the percentage likelihood of the image being AI-generated.
#
# BASH Team:
#   Adela Mihaela Jianu
#   Blake Yang Hu
#   Shirley Zhang
# 
#   Northwestern University
#   CS 310, Final Project
#

import pathlib
import base64
import logging
import requests
import json
import uuid
import pathlib
import logging
import sys
import os

from configparser import ConfigParser

import matplotlib.pyplot as plt
import matplotlib.image as img

############################################################
#
# prompt
#
def prompt():
  """
  Prompts the user and returns the command number

  Parameters
  ----------
  None

  Returns
  -------
  Command number entered by user (0, 1, 2, ...)
  """

  print()
  print(">> Enter a command:")
  print("   0 => end")
  print("   1 => upload")
  print("   2 => retrieve")

  cmd = input()

  if cmd == "":
    cmd = -1
  elif not cmd.isnumeric():
    cmd = -1
  else:
    cmd = int(cmd)

  return cmd

############################################################
#
# upload
#
def upload(baseurl):
  """
  Prompts the user for a local filename, 
  and uploads that asset (jpg/jpeg/png) to S3 for processing. 

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  image_id: id of the uploaded image
  """

  print()
  print("Enter filename>")
  local_filename = input()

  if not pathlib.Path(local_filename).is_file():
    print("file '", local_filename, "' does not exist...")
    return

  try:
    #
    # build the data packet:
    #
    infile = open(local_filename, "rb")
    bytes = infile.read()
    infile.close()

    #
    # now encode the image as base64. Note b64encode returns
    # a bytes object, not a string. So then we have to convert
    # (decode) the bytes -> string, and then we can serialize
    # the string as JSON for upload to server:
    #
    data = base64.b64encode(bytes)
    datastr = data.decode()

    data = {"filename": local_filename, 
            "data": datastr}

    #
    # call the web service:
    #
    api = '/upload'
    url = baseurl + api
    res = requests.post(url, json=data)

    body = res.json()

    #
    # let's look at what we got back:
    #
    if res.status_code != 200:
      print()
      print(body)
      #
      return

    #
    # return message
    #
    print()
    print("uploaded: ", body["imageID"])
    print("**Save the above number, this is your imageid. Run predictions to see the ai prediction on this image.**")
    return

  except Exception as e:
    logging.error("upload() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return
  
############################################################
#
# retrieve
#
def retrieve(baseurl):
  """
  Prompts the user for the image id, and returns the
  that percentage of the image being ai generated 
  and opens the image in a pop up tab to remind 
  the user of the image for which information is
  being returned. If the imageid has not finished
  calculating, then a status of pending is returned.

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  status: returned only when pending or error
  percentage_ai: returned when status is complete
  """

  print()
  print("Enter image id>")
  imageid = input()

  try:
    #
    # call the web service:
    #
    api = '/retrieve'
    url = baseurl + api + '/' + imageid

    res = requests.get(url)

    #
    # let's look at what we got back:
    #

    body = res.json()

    if (res.status_code != 200):
      print()
      print(body, "please check your imageid or reupload your image")
      #
      return

    print()
    print("Filename   : " ,body["file_name"])
    if (body["status"] != "complete"):
      # print status if pending
      print("Status     : ", body["status"])
    else:
      # output percentage if status complete
      print("Percentage : ", body["precentage_ai"])
      print("** The likelihood of", body["file_name"], "being ai generated is", body["precentage_ai"], "% **")
      print()
      print("Close your image to continue")

      #
      # retrieve the image
      #
      datastr = body["image"]

      bytes = base64.b64decode(datastr)

      filename = body["file_name"]

      #
      # write the binary data to a file (as a
      # binary file, not a text file):
      #
      outfile = open(filename, "wb")
      outfile.write(bytes)
      outfile.close()
  
      display = True

      if display:
        image = img.imread(filename)
        plt.imshow(image)
        plt.show()

    return
    

  except Exception as e:
    logging.error("retrieve() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return
  
############################################################
# main
#
try:
  print()
  print('**                     Welcome to the BASH: AI Image Detection App                   **')
  print('** This app will tell you the percentage likelihood of your image being AI generated **')
  print('**                                                                                   **')
  print('**                First upload your image, then retrieve your results                **')
  print('**            It may take a few seconds, if your status is pending, retry            **')
  print('**                     This app only takes jpg, jpeg, png files                      **')
  print()
  
  baseurl= f"https://rce057rit7.execute-api.us-east-2.amazonaws.com/prod"

  # prompt the user to upload or retrieve
  cmd = prompt()

  while cmd != 0:
    if cmd == 1:
      upload(baseurl)
    elif cmd == 2:
      retrieve(baseurl)
    else:
      print("** Unknown command, try again...")
    cmd = prompt()

except Exception as e:
  logging.error("**ERROR: main() failed:")
  logging.error(e)
  sys.exit(0)