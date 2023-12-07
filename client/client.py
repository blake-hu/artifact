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
  print("   1 => images")
  print("   2 => predictions")
  print("   3 => upload")
  print("   4 => retrieve")
  print("   5 => stats")

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
  and uploads that asset (jpg/png) to S3 for processing. 

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  nothing
  """

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

    #
    # let's look at what we got back:
    #
    if res.status_code != 200:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 400:
        # we'll have an error message
        body = res.json()
        print("Error message:", body)
      #
      return
    
    body = res.json()

    # return message
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
  that percentage of the image being ai generated.

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  nothing
  """

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

    if res.status_code != 200:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 400:
        # we'll have an error message
        body = res.json()
        print("Error message:", body)
      #
      return

    print("Filename : " ,body["file_name"])
    if (body["status"] != "complete"):
      # print status if pending
      print("Status   : ", body["status"])
    else:
      # output percentage if status complete
      print("Percentage : ", body["precentage_ai"])
    return

  except Exception as e:
    logging.error("retrieve() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return
  
############################################################
# main
#
# def main():
try:
  baseurl= f"https://rce057rit7.execute-api.us-east-2.amazonaws.com/prod"

  cmd = prompt()

  while cmd != 0:
    if cmd == 1:
      users(baseurl)
    elif cmd == 2:
      jobs(baseurl)
    elif cmd == 3:
      upload(baseurl)
    elif cmd == 4:
      retrieve(baseurl)
    elif cmd == 5:
      reset(baseurl)
    else:
      print("** Unknown command, try again...")
    cmd = prompt()

except Exception as e:
  logging.error("**ERROR: main() failed:")
  logging.error(e)
  sys.exit(0)

# if __name__ == "__main__":
#    main()