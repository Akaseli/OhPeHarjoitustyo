import json
from datetime import datetime
from elokuva import haeElokuva
from sali import haeSali

def haeNaytokset():
  with open("data/naytokset.json", "r+") as file:
    data = json.load(file)
    return data
  
def teeVaraus(index, nimi):
  with open("data/naytokset.json", "r") as file:
    data = json.load(file)

  data[index]["varaukset"].append(nimi)

  with open("data/naytokset.json", "w") as file:
    json.dump(data, file, indent=4)
  
  

def luoNaytos(elokuva:str, sali:int, naytoksenAika:str):
  with open("data/naytokset.json", "r") as file:
    data = json.load(file)

  try:
    date = datetime.strptime(naytoksenAika, "%d/%m/%Y %H:%M")
    kesto = haeElokuva(elokuva)["kesto"]
    
    minuutit, sekuntit = divmod(kesto, 60)
    tunnit, minuutit = divmod(minuutit, 60)

    timeStr = str(tunnit) + "h " + str(minuutit) + "min"
  except:
    return False
  
  data.append({"nimi":elokuva, "aika":date.timestamp(), "kesto":timeStr, "sali":sali, "varaukset":[]})


  with open("data/naytokset.json", "w") as file:
    json.dump(data, file, indent=4)

  return True


def poistaNaytos(index):
  with open("data/naytokset.json", "r") as file:
    data = json.load(file)

  data.pop(index)
  
  with open("data/naytokset.json", "w") as file:
    json.dump(data, file, indent=4)