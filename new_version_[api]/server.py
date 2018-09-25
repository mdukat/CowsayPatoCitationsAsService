#!/usr/bin/python
import socket
import time
import subprocess
import thread
import sys
from random import randint
from os import listdir

port_krowy = 22137
port_statystyk = 14488

typy_krow = ['apt', 'bud-frogs', 'bunny', 'calvin', 'cheese', 'cock', 'cower', 'daemon', 'default', 'dragon', 'dragon-and-cow', 'duck', 'elephant', 'elephant-in-snake', 'eyes', 'flaming-sheep', 'ghostbusters', 'gnu', 'hellokitty', 'kiss', 'koala', 'kosh', 'luke-koala', 'mech-and-cow', 'milk', 'moofasa', 'moose', 'pony', 'pony-smaller', 'ren', 'sheep', 'skeleton', 'snowman', 'stegosaurus', 'stimpy', 'suse', 'three-eyes', 'turkey', 'turtle', 'tux', 'unipony', 'unipony-smaller', 'vader', 'vader-koala', 'www']

wiadomosc_help = "aaaaaaaaaa"

def outputuj(tekst):
	tekst = time.strftime("[%d/%m/%Y %H:%M:%S] ") + tekst
	print tekst
	subprocess.call(["./loguj.sh", tekst])

class SerwerStatystyk(object):
	def __init__(self, socket_address, socket_port, krowa_obj):
		self.liczba_requestow = 0
		self.krowa_obj = krowa_obj
		self.sock = socket.socket()
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind((socket_address, socket_port))
		thread.start_new_thread(self.listenuj, ())

	def listenuj(self):
		self.sock.listen(20)
		while True:
			self.client, self.c_addr = self.sock.accept()
			self.client.settimeout(2)
			thread.start_new_thread(self.handleUser, (self.client, self.c_addr, self.krowa_obj))

	def handleUser(self, client, c_addr, krowa_obj):
		query = client.recv(1024)
		response = "a"
		if (query[0:3] == 'GET'):
			response = "HTTP/1.1 200 OK\nContent-Type: text; charset=UTF-8\n\n" + "Requestow do tej pory: " + krowa_obj.iloscRequestow() + "\n"
			outputuj("Wysylam statystyke do " + c_addr[0])
			krowa_obj.dodajRequest()
		if (query[0:3] == 'POST'):
			response = wiadomosc_help
			outputuj("Wysylam help do " + c_addr[0])
			krowa_obj.dodajRequest()
		client.sendall(response)
		client.close()
	
	def zabijObiekt(self):
		self.sock.close()
		outputuj("Zamykam serwer statystyk")

class SerwerKrowy(object):
	def __init__(self, socket_address, socket_port):
		self.liczba_requestow = 0
		self.sock = socket.socket()
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind((socket_address, socket_port))
		thread.start_new_thread(self.listenuj, ())

	def listenuj(self):
		self.sock.listen(20)
		while True:
			self.client, self.c_addr = self.sock.accept()
			self.client.settimeout(2)
			thread.start_new_thread(self.handleUser, (self.client, self.c_addr,))

	def handleUser(self, client, c_addr):
		query = client.recv(1024)
		if (query[0:3] == 'GET'):
			response = "HTTP/1.1 200 OK\nContent-Type: text; charset=UTF-8\n\n" + self.wywolajKrowe(self.losujTekst(None), None)
			outputuj("Wysylam losowy tekst do " + c_addr[0])
			self.liczba_requestow += 1
		elif (query[0:4] == 'POST'):
			#API
			autor = None
			krowa = None
			argumenty = query[query.find('args:'):][5:]
			if(len(argumenty) >= 50):
				response = "zbyt duzo argumentow"
			else:
				argumenty = argumenty.split(';')
				for argument in argumenty:
					if (argument[0:5] == "autor"):
						wartosc = argument.split('=')[1]
						autor = wartosc
					if (argument[0:5] == "krowa"):
						wartosc = argument.split('=')[1]
						krowa = wartosc
				response = "HTTP/1.1 200 OK\nContent-Type: text; charset=UTF-8\n\n" + self.wywolajKrowe(self.losujTekst(autor), krowa)
				if (autor == None):
					autor = "RandomAutor"
				if (krowa == None):
					krowa = "DefaultKrowa"
				outputuj("[API] Wysylam tekst " + autor + " w krowie " + krowa + " do " + c_addr[0])
				self.liczba_requestow += 1
		else:
			response = "error"
		client.sendall(response)
		client.close()

	def zabijObiekt(self):
		self.sock.close()
		outputuj("Zamykam serwer krowy")

	def wywolajKrowe(self, tekst, typ):
		if (typ == None):
			typ = 8
		if (typ == "random"):
			typ = randint(0, len(typy_krow)-1)
		else:
			try:
				typ = typy_krow.index(typ)
			except ValueError:
				typ = 8
		return subprocess.check_output(['cowsay', '-f', typy_krow[typ], tekst])

	def losujTekst(self, autor):
		if (autor == None):
			#losowy
			pliki = listdir('./teksty')
			autor = "./teksty/" + pliki[randint(0,len(pliki)-1)]
			plik = open(autor)
			cytaty = plik.readlines()
			plik.close()
			cytat = cytaty[randint(0,len(cytaty)-1)]
		else:
			try:
				plik_a = "./teksty/" + autor
				plik = open(plik_a)
				cytaty = plik.readlines()
				plik.close()
				cytat = cytaty[randint(0,len(cytaty)-1)]
			except:
				cytat = self.losujTekst(None)
		cytat = "\"" + cytat + "\" ~" + autor.split('/')[-1]
		return cytat

	def iloscRequestow(self):
		return str(self.liczba_requestow)

	def dodajRequest(self):
		self.liczba_requestow += 1

def main():
	try:
		outputuj("Start serwera")
		krowiserwer = SerwerKrowy('', port_krowy)
		statystycznyserwer = SerwerStatystyk('', port_statystyk, krowiserwer)
		while True:
			pass
	except KeyboardInterrupt:
		outputuj("Wykonanych requestow w tej sesji: " + krowiserwer.iloscRequestow())
		outputuj("Zabijam serwery")
		krowiserwer.zabijObiekt()
		statystycznyserwer.zabijObiekt()
		outputuj("Wychodze")
		sys.exit(0)

main()
