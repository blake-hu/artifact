import pathlib
import base64
import logging
import requests

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
    print("uploaded")
    return

  except Exception as e:
    logging.error("upload() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return
  
def main():
  baseurl= f"https://rce057rit7.execute-api.us-east-2.amazonaws.com/prod"
  upload(baseurl)


if __name__ == "__main__":
   main()