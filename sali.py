import json

def haeSali(numero):
  with open("data/salit.json", "r+") as file:
    data = json.load(file)
  
    try:
      sali = data[str(numero)]
      return sali
    except:
      return False

def haeSalit():
  with open("data/salit.json", "r+") as file:
    data = json.load(file)
  
  return data


def luoSali(numero, rivit, paikkojaPerRivi):
  with open("data/salit.json", "r") as file:
    data = json.load(file)

  if not str(numero) in data:
    data[numero] = {"riveja": rivit, "paikkojaPerRivi": paikkojaPerRivi}
  
  with open("data/salit.json", "w") as file:
    json.dump(data, file, indent=4)

  return True
    

def poistaSali(numero):
  with open("data/salit.json", "r") as file:
    data = json.load(file)

  data.pop(str(numero), None)
  
  with open("data/salit.json", "w") as file:
    json.dump(data, file, indent=4)


