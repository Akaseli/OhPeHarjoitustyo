import tkinter as tk
from tkinter import ttk, messagebox

from elokuva import *
from naytos import *
from sali import *

class App(tk.Tk):
  def __init__(self):
    tk.Tk.__init__(self)
    self.title("Elokuvateatterisofta v1")

    self.sivut = {}

    for sivu in (Etusivu, Adminsivu):
      frame = sivu(self)
      self.sivut[sivu] = frame
      frame.place(relx=0, rely=0, relwidth=1, relheight=1)
    
    #Ylä palkin navigointi
    topbar = tk.Menu(self)
    komentoMenu = tk.Menu(topbar, tearoff=0)
    komentoMenu.add_command(label="Admin-tila", command=lambda: self.naytaSivu(Adminsivu))
    komentoMenu.add_command(label="Käyttäjä-tila", command=lambda: self.naytaSivu(Etusivu))
    topbar.add_cascade(label="Komennot", menu=komentoMenu)

    # Ikkunan muoto + palkki käyttöön
    self.geometry("1020x600")
    self.config(menu=topbar)

    #Näytetään etusivu
    self.naytaSivu(Etusivu)


  def naytaSivu(self, frame):
    frame = self.sivut[frame]
    #Paivitetään sivun sisältö
    frame.update()
    #Nostetaan näkyville
    frame.tkraise()

class Etusivu(tk.Frame):
  def __init__(self, parent):
    tk.Frame.__init__(self, parent)

    label = tk.Label(self, text="Tulevat näytökset")
  
    #Lista
    columns = ("nimi", "alku", "kesto", "sali", "varaukset")
    self.tree = ttk.Treeview(self, columns=columns, show="headings")

    self.tree.heading("nimi", text="Elokuvan nimi")
    self.tree.heading("alku", text="Näytöksen aika")
    self.tree.heading("kesto", text="Kesto")
    self.tree.heading("sali", text="Salin numero")
    self.tree.heading("varaukset", text="Vapaana")

    self.tree.bind("<<TreeviewSelect>>", self.select)

    #Varaus juttu
    self.varaus = tk.Frame(self)
    self.valittu = tk.Label(self.varaus, text="Näytös: ", anchor="w", width=30)
    self.paikat = tk.Label(self.varaus, text="Vapaita paikkoja: ", anchor="w", width=30)
    self.varausnimiLabel = tk.Label(self.varaus, text="Varauksen nimi")
    self.varausnimi = tk.Text(self.varaus, height = 1, width = 50)
    self.varaaNappi = tk.Button(self.varaus, text="Varaa", state="disabled")


    #Asettelu
    label.grid(row=0, column=0, sticky="n")
    scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
    self.tree.configure(yscroll=scrollbar.set)

    label.grid(row=0, column=0, sticky="n")
    self.tree.grid(row=1, column=0, sticky="nsew")
    scrollbar.grid(row=1, column=1, sticky="ns")
    
    self.varaus.grid(row=2, column=0, sticky="w")
    #Varaus
    self.valittu.grid(row=1, column=0, sticky="w")
    self.paikat.grid(row=1, column=1, sticky="w")
    self.varausnimiLabel.grid(row=2, column=0, sticky="e")
    self.varausnimi.grid(row=2, column=1, sticky="w")
    self.varaaNappi.grid(row=2, column=2, sticky="w")

  def paivitaLista(self):
    #Poista vanhat
    for n in self.tree.get_children():
      self.tree.delete(n)

    #Naytosten sijoitus listaan
    self.naytokset = haeNaytokset()
    self.naytokset.sort(key=lambda x: x["aika"])
      
    for naytos in self.naytokset:
      sali = haeSali(naytos["sali"])
      aika = datetime.fromtimestamp(naytos["aika"])

      paikkoja = int(sali["riveja"]) * int(sali["paikkojaPerRivi"])
      self.tree.insert("", tk.END, values=(naytos["nimi"], aika.strftime("%d/%m/%Y %H:%M"), naytos["kesto"], naytos["sali"], "{}/{}".format(paikkoja-len(naytos["varaukset"]), paikkoja)))

  #Näytöslistan valinta event
  def select(self, e):
    if len(self.tree.selection()) > 0:
      index = self.tree.index(self.tree.selection()[0])
      naytos = self.naytokset[index]

      sali = haeSali(naytos["sali"])
      paikkoja = int(sali["riveja"]) * int(sali["paikkojaPerRivi"])

      self.valittu.config(text=("Näytös: " + naytos["nimi"]))
      self.paikat.config(text=("Vapaita paikkoja: " + str(paikkoja - len(naytos["varaukset"]))))
      self.varaaNappi.config(command=lambda: self.varaa(index), state="normal")
    else:
      self.valittu.config(text=("Näytös: "))
      self.paikat.config(text=("Vapaita paikkoja: "))
      self.varausnimi.delete("1.0", tk.END)
      self.varaaNappi.config(state="disabled")

  def varaa(self, index):
    self.naytokset[index]
    naytos = self.naytokset[index]

    sali = haeSali(naytos["sali"])
    paikkoja = int(sali["riveja"]) * int(sali["paikkojaPerRivi"])
    tilaa = paikkoja - len(naytos["varaukset"])

    if(tilaa < 1):
      messagebox.showerror("Elokuvateatterisofta v1", "Error: Näytös on täynnä")
    elif len(self.varausnimi.get("1.0", "end-1c"))>0:
      teeVaraus(index, self.varausnimi.get("1.0", "end-1c"))
      self.paivitaLista()
    else:
      messagebox.showerror("Elokuvateatterisofta v1", "Error: Tarkista syöte")

  # Kutsutaan aina sivun vaihtuessa
  def update(self):
    self.paivitaLista()
    #Resetoidaan inputit
    self.valittu.config(text=("Näytös: "))
    self.paikat.config(text=("Vapaita paikkoja: "))
    self.varausnimi.delete("1.0", tk.END)
    self.varaaNappi.config(state="disabled")


class Adminsivu(tk.Frame):
  def __init__(self, parent):
    tk.Frame.__init__(self, parent)
    
    label = tk.Label(self, text="Admin-sivu")
    
    self.viimeisinElokuva = ""
    self.viimeisinSali = ""

    #Naytoslista
    naytosHallinta = tk.Frame(self)
    naytosTitle = tk.Label(naytosHallinta, text="Näytös hallinta")
    columns = ("nimi", "alku", "kesto", "sali", "varaukset")
    self.tree = ttk.Treeview(naytosHallinta, columns=columns, show="headings")

    self.tree.heading("nimi", text="Elokuvan nimi")
    self.tree.heading("alku", text="Näytöksen aika")
    self.tree.heading("kesto", text="Kesto")
    self.tree.heading("sali", text="Salin numero")
    self.tree.heading("varaukset", text="Vapaana")

    self.tree.bind("<<TreeviewSelect>>", self.treeSelect)
    scrollbar = tk.Scrollbar(naytosHallinta, orient=tk.VERTICAL, command=self.tree.yview)
    self.tree.configure(yscroll=scrollbar.set)
    
    alasivut = tk.Frame(self)

    #Valitun näytöksen varaukset
    varaukset = tk.Frame(alasivut)
    vLabel = tk.Label(varaukset, text="Varaukset")
    self.vLista = tk.Listbox(varaukset, height=7)
    vScroll = tk.Scrollbar(varaukset, orient=tk.VERTICAL, command=self.vLista.yview)
    self.vLista.configure(yscroll=vScroll.set)
    self.poistaNaytosButton = tk.Button(varaukset, text="Poista valittu näytös", state="disabled")

    #Elokuvan luonti
    elokuvanLuonti = tk.Frame(alasivut)
    eLuoLabel = tk.Label(elokuvanLuonti, text="Luo elokuva")
    eNimiLabel = tk.Label(elokuvanLuonti, text="Elokuvan nimi")
    self.elokuvanNimi = tk.Text(elokuvanLuonti, height = 1, width = 20)
    eLuoKesto = tk.Label(elokuvanLuonti, text="Elokuvan kesto (h:min, esim. 2:15)")
    self.elokuvanKesto = tk.Text(elokuvanLuonti, height = 1, width = 20)
    self.eLuoNappi = tk.Button(elokuvanLuonti, text="Luo elokuva", command=lambda: self.luoUusiElokuva())

    #Salin luonti
    saliLuonti = tk.Frame(alasivut)
    sLuoLabel = tk.Label(saliLuonti, text="Luo sali")
    sNumeroLabel = tk.Label(saliLuonti, text="Salin numero")
    self.sNumero = tk.Spinbox(saliLuonti, from_=1, to=99)
    sRivejaLabel = tk.Label(saliLuonti, text="Rivejä")
    self.riviNumero = tk.Spinbox(saliLuonti, from_=1, to=99)
    sPaikkojaLabel = tk.Label(saliLuonti, text="Paikkoja rivillä")
    self.rpaikkaNumero = tk.Spinbox(saliLuonti, from_=1, to=99)
    self.luoSaliButton = tk.Button(saliLuonti, text="Luo sali", command=lambda: self.luoSali())

    #Salin poisto
    salit = tk.Frame(alasivut)
    sLabel = tk.Label(salit, text="Salien hallinta")
    self.sLista = tk.Listbox(salit, height=7)
    sScroll = tk.Scrollbar(salit, orient=tk.VERTICAL, command=self.sLista.yview)
    self.sLista.configure(yscroll=sScroll.set)
    self.sLista.bind("<<ListboxSelect>>", self.saliSelect)
    self.sDelButton = tk.Button(salit, text="Poista sali", state="disabled")

    #Elokuvan poisto
    elokuvat = tk.Frame(alasivut)
    eLabel = tk.Label(elokuvat, text="Elokuvien hallinta")
    self.eLista = tk.Listbox(elokuvat, height=7)
    eScroll = tk.Scrollbar(elokuvat, orient=tk.VERTICAL, command=self.eLista.yview)
    self.eLista.configure(yscroll=eScroll.set)
    self.eLista.bind("<<ListboxSelect>>", self.elokuvaSelect)
    self.eDelButton = tk.Button(elokuvat, text="Poista elokuva", state="disabled")
    
    
    #Näytöksen luonti
    naytosLuonti = tk.Frame(alasivut)
    nLuoLabel = tk.Label(naytosLuonti, text="Luo näytös (Valitse haluttu elokuva ja sali listoista)")
    self.nSaliLabel = tk.Label(naytosLuonti, text="Valittu sali: ", anchor="w", width=30)
    self.nElokuvaLabel = tk.Label(naytosLuonti, text="Valittu elokuva: ", anchor="w", width=30)
    nAika = tk.Label(naytosLuonti, text="Näytöksen aika (pv/kk/v h:min, esim 13/1/2024 14:00)")
    self.nAikaInput = tk.Text(naytosLuonti, height = 1, width = 20)
    self.nLuoButton = tk.Button(naytosLuonti, text="Luo näytös", command=lambda: self.luoNaytos())
    

    # ASETTELU
    label.grid(row=0, column=0, sticky="n")
    naytosHallinta.grid(row=0, column=0, sticky="n")
    alasivut.grid(row=1, column=0, sticky="wn")
    

    varaukset.grid(row=0, column=0, sticky="wn", padx=10)
    saliLuonti.grid(row=0, column=1, sticky="wn", padx=10)
    elokuvanLuonti.grid(row=1, column=1, sticky="wn", padx=10)
    salit.grid(row=0, column=2, sticky="wn", padx=10)
    elokuvat.grid(row=1, column=2, sticky="wn", padx=10)
    naytosLuonti.grid(row=0, column=3, sticky="wn", padx=10)

    #Näytös hallinta
    naytosTitle.grid(row=0, column=0, sticky="n")
    label.grid(row=0, column=0, sticky="n")
    self.tree.grid(row=1, column=0, sticky="nsew")
    scrollbar.grid(row=1, column=1, sticky="ns")
    self.poistaNaytosButton.grid(row=2, column=0, sticky="w")
    #Varaukset
    vLabel.grid(row=0, column=0, sticky="w")
    self.vLista.grid(row=1, column=0, sticky="n")
    vScroll.grid(row=1, column=1, sticky="ns")

    #Salin luonti
    sLuoLabel.grid(row=0, column=0, sticky="w")
    sNumeroLabel.grid(row=1, column=0, sticky="w")
    self.sNumero.grid(row=2, column=0, sticky="w")
    sRivejaLabel.grid(row=3, column=0, sticky="w")
    self.riviNumero.grid(row=4, column=0, sticky="w")
    sPaikkojaLabel.grid(row=5, column=0, sticky="w")
    self.rpaikkaNumero.grid(row=6, column=0, sticky="w")
    self.luoSaliButton.grid(row=7, column=0, sticky="w")

    #Elokuvan luonti
    eLuoLabel.grid(row=0, column=0, sticky="w")
    eNimiLabel.grid(row=1, column=0, sticky="w")
    self.elokuvanNimi .grid(row=2, column=0, sticky="w")
    eLuoKesto.grid(row=3, column=0, sticky="w")
    self.elokuvanKesto.grid(row=4, column=0, sticky="w")
    self.eLuoNappi.grid(row=5, column=0, sticky="w")

    #Salit
    sLabel.grid(row=0, column=0, sticky="w")
    self.sLista.grid(row=1, column=0, sticky="n")
    sScroll.grid(row=1, column=1, sticky="ns")
    self.sDelButton.grid(row=2, column=0, sticky="w")

    #Elokuvat
    eLabel.grid(row=0, column=0, sticky="w")
    self.eLista.grid(row=1, column=0, sticky="n")
    eScroll.grid(row=1, column=1, sticky="ns")
    self.eDelButton.grid(row=2, column=0, sticky="w")

    #Näytöksen luonti
    nLuoLabel.grid(row=0, column=0, sticky="w")
    self.nSaliLabel.grid(row=1, column=0, sticky="w")
    self.nElokuvaLabel.grid(row=2, column=0, sticky="w")
    nAika.grid(row=3, column=0, sticky="w")
    self.nAikaInput.grid(row=4, column=0, sticky="w")
    self.nLuoButton.grid(row=5, column=0, sticky="w")

  #Elokuva funktiot
  def poistaElokuva(self, nimi):
    for naytos in haeNaytokset():
      if naytos["nimi"] == nimi:
        messagebox.showerror("Elokuvateatterisofta v1", "Error: Elokuvaa ei voida poistaa, mikäli sitä esitetään.")
        break
    else:
      poistaElokuva(nimi)
      self.eDelButton.config(state="disabled")
      self.nElokuvaLabel.config(text="Valittu elokuva: ")
      self.paivitaElokuvaLista()


  def luoUusiElokuva(self):
    if not luoElokuva(self.elokuvanNimi.get("1.0", "end-1c"), self.elokuvanKesto.get("1.0", "end-1c")):
      messagebox.showerror("Elokuvateatterisofta v1", "Error: Tarkista syöteen muoto")
    else:
      self.elokuvanNimi.delete("1.0", tk.END)
      self.elokuvanKesto.delete("1.0", tk.END)
      self.paivitaElokuvaLista()

  def elokuvaSelect(self, e):
   if(len(e.widget.curselection()) > 0):
     index = e.widget.curselection()[0]
     elokuva = e.widget.get(index)
     self.viimeisinElokuva = elokuva
     
     self.eDelButton.config(state="active", command=lambda: self.poistaElokuva(elokuva))
     self.nElokuvaLabel.config(text="Valittu elokuva: " + elokuva)

  def paivitaElokuvaLista(self):
    self.eLista.delete(0, tk.END)

    elokuvat = haeElokuvat()
    for elokuva in elokuvat.keys():
      self.eLista.insert(tk.END, elokuva)

  #Sali funktiot
  def luoSali(self):
    try:
      saliNro = int(self.sNumero.get())
      riveja = int(self.riviNumero.get())
      paikkojaRivilla = int(self.rpaikkaNumero.get())
    except:
      messagebox.showerror("Elokuvateatterisofta v1", "Error: Tarkista syöteen muoto")
      return

    if not haeSali(saliNro):
      luoSali(saliNro, riveja, paikkojaRivilla)
      self.paivitaSaliLista()
      self.sNumero.delete(0, tk.END)
      self.riviNumero.delete(0, tk.END)
      self.rpaikkaNumero.delete(0, tk.END)
      self.sNumero.insert(0, 1)
      self.riviNumero.insert(0, 1)
      self.rpaikkaNumero.insert(0, 1)
    else:
      messagebox.showerror("Elokuvateatterisofta v1", "Error: Kyseinen numero on käytössä")
  
  def saliSelect(self, e):
    if(len(e.widget.curselection()) > 0):
      index = e.widget.curselection()[0]
      saliNro = e.widget.get(index).split(" ")[1]
      self.viimeisinSali = saliNro
      
      self.sDelButton.config(state="active", command=lambda: self.poistaSali(saliNro))
      self.nSaliLabel.config(text="Luodaan näytöstä saliin: " + saliNro)

  def poistaSali(self, numero):
    for naytos in haeNaytokset():
      if naytos["sali"] == int(numero):
        messagebox.showerror("Elokuvateatterisofta v1", "Error: Salia ei voida poistaa, mikäli siellä on näytöksiä")
        break
    else:
      poistaSali(numero)
      self.sDelButton.config(state="disabled")
      self.nSaliLabel.config(text="Luodaan näytöstä saliin: ")
      self.paivitaSaliLista()


  def paivitaSaliLista(self):
    self.sLista.delete(0, tk.END)

    salit = haeSalit()
    for sali in salit.keys():
      self.sLista.insert(tk.END, "Sali " + str(sali)+ " (" + str(salit[sali]["riveja"]*salit[sali]["paikkojaPerRivi"]) + " paikkaa)")

  # Näytös funktiot
  def treeSelect(self, e):
    if len(self.tree.selection()) > 0:
      index = self.tree.index(self.tree.selection()[0])
      naytos = self.naytokset[index]

      self.vLista.delete(0, tk.END)

      for varaus in naytos["varaukset"]:
        self.vLista.insert(tk.END, varaus)
      
      self.poistaNaytosButton.config(state="normal", command=lambda: self.poistaNaytos(index))

    else:
      self.vLista.delete(0, tk.END)
      self.poistaNaytosButton.config(state="disabled")

  def paivitaNaytosLista(self):
    #Poista vanhat
    for n in self.tree.get_children():
      self.tree.delete(n)

    #Naytosten sijoitus listaan
    self.naytokset = haeNaytokset()
    self.naytokset.sort(key=lambda x: x["aika"])
      
    for naytos in self.naytokset:
      sali = haeSali(naytos["sali"])
      aika = datetime.fromtimestamp(naytos["aika"])

      paikkoja = int(sali["riveja"]) * int(sali["paikkojaPerRivi"])
      self.tree.insert("", tk.END, values=(naytos["nimi"], aika.strftime("%d/%m/%Y %H:%M"), naytos["kesto"], naytos["sali"], "{}/{}".format(paikkoja-len(naytos["varaukset"]), paikkoja)))

  def luoNaytos(self):
    if not luoNaytos(self.viimeisinElokuva, self.viimeisinSali, self.nAikaInput.get("1.0", "end-1c")):
      messagebox.showerror("Elokuvateatterisofta v1", "Error: Tarkista syöteen muoto")
    else:
      self.nAikaInput.delete("1.0", tk.END)
      self.nElokuvaLabel.config(text="Valittu elokuva: ")
      self.nSaliLabel.config(text="Luodaan näytöstä saliin: ")
      self.paivitaNaytosLista()

  def poistaNaytos(self, index):
    poistaNaytos(index)
    self.paivitaNaytosLista()

  # Kutsutaan aina sivun vaihtuessa
  def update(self):
    self.paivitaNaytosLista()
    self.paivitaSaliLista()
    self.paivitaElokuvaLista()
    #Resetoidaan inputit
    
    #Sali
    self.sDelButton.config(state="disabled")
    self.nSaliLabel.config(text="Luodaan näytöstä saliin: ")
    

    #Elokuva
    self.nElokuvaLabel.config(text="Valittu elokuva: ")
    self.paivitaElokuvaLista()

    self.eDelButton.config(state="disabled")
    self.elokuvanNimi.delete("1.0", tk.END)
    self.elokuvanKesto.delete("1.0", tk.END)

    #Näytös
    self.nAikaInput.delete("1.0", tk.END)

root = App()
root.mainloop()