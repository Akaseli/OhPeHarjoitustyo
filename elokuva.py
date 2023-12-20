import json

def haeElokuva(nimi):
  with open("data/elokuvat.json", "r+") as file:
    data = json.load(file)
  
    try:
      elokuva = data[nimi]
      return elokuva
    except:
      return False
    
def haeElokuvat():
  with open("data/elokuvat.json", "r+") as file:
    data = json.load(file)
  
  return data
  
def luoElokuva(nimi, kesto):
  with open("data/elokuvat.json", "r") as file:
    data = json.load(file)

  try:  
    aika = kesto.split(":")
    sekunnit = int(aika[0]) * 3600 + int(aika[1]) * 60
  except:
    return False
  
  if not nimi in data:
    data[nimi] = {"kesto": sekunnit}
  else:
    return False
  
  with open("data/elokuvat.json", "w") as file:
    json.dump(data, file, indent=4)
  
  return True


def poistaElokuva(nimi):
  with open("data/elokuvat.json", "r") as file:
    data = json.load(file)

  data.pop(nimi, None)
  
  with open("data/elokuvat.json", "w") as file:
    json.dump(data, file, indent=4)
