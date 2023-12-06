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

def upload(baseurl):
  """
  Prompts the user for a local filename and user id, 
  and uploads that asset (PDF) to S3 for processing. 

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
    # now encode the pdf as base64. Note b64encode returns
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
    print(url)
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

    print("uploaded: ", body["imageID"])
    print("**Save the above number, this is your imageid. Run predictions to see the ai prediction on this image.**")
    return

  except Exception as e:
    logging.error("upload() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return
  
  # ############################################################
# #
# # download
# #
def download(baseurl):
  """
  Prompts the user for the job id, and downloads
  that asset (PDF).

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  nothing
  """

  print("Enter job id>")
  jobid = input()

  try:
    #
    # call the web service:
    #
    api = '/download'
    url = baseurl + api + '/' + jobid

    res = requests.get(url)

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

    #
    # deserialize and extract results:
    #
    body = res.json()

    datastr = body

    base64_bytes = datastr.encode()
    bytes = base64.b64decode(base64_bytes)
    results = bytes.decode()

    print(results)
    return

  except Exception as e:
    logging.error("download() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return
  
def main():
  baseurl= f"https://rce057rit7.execute-api.us-east-2.amazonaws.com/prod"
  #upload(baseurl)
  cmd = prompt()

  while cmd != 0:
    #
    if cmd == 1:
      users(baseurl)
    elif cmd == 2:
      jobs(baseurl)
    elif cmd == 3:
      upload(baseurl)
    elif cmd == 4:
      download(baseurl)
    elif cmd == 5:
      reset(baseurl)
    else:
      print("** Unknown command, try again...")

  #  def main():
  # print()
  # print(">> Enter a command:")
  # print("   0 => end")
  # print("   1 => images")
  # print("   2 => predictions")
  # print("   3 => upload")
  # print("   4 => retrieve")
  # print("   5 => stats")

  # cmd = input()

  # baseurl= f"https://rce057rit7.execute-api.us-east-2.amazonaws.com/prod"

  # while cmd != 0:
  #   #
  #   if cmd == 1:
  #     pass
  #   elif cmd == 2:
  #     pass
  #   elif cmd == 3:
  #     upload(baseurl)
  #   elif cmd == 4:
  #     pass
  #   elif cmd == 5:
  #     pass
  #   else:
  #     print("** Unknown command, try again...")
  #   #cmd = prompt()

  #   print('** done **')
  #  # upload(baseurl)


if __name__ == "__main__":
   main()