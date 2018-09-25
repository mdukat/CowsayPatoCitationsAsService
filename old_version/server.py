import socket
import subprocess
import thread
import time

port = 14488
log_plik = open("rychuService.log", "ab")

def wywal(tekst):
	tekst = time.strftime("[%d/%m/%Y %H:%M:%S]") + tekst
	print(tekst)
	try:
		log_plik.write(tekst + "\n")
	except:
		print("Error wpisu do logu")

def wyslijRysia(client, c_addr):
	wywal("Wysylam rysia do " + c_addr[0])
	client.send(subprocess.check_output(['./rysiu.sh']))
	client.close()

def main():
	wywal("Uruchamiam serwer")
	my_sock = socket.socket()
	my_sock.bind(('', port))
	my_sock.listen(5)
	wywal("Czekam na polaczenia")
	while 1:
		client, c_addr = my_sock.accept()
		thread.start_new_thread(wyslijRysia, (client, c_addr,))

main()

