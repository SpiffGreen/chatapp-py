from dotenv import dotenv_values
config = dotenv_values(".env")

def getConfig():
  return config