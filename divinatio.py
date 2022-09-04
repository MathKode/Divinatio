import argparse
from os import stat

parser = argparse.ArgumentParser(
	description="Code qui génère une liste de mot de passe possible à partir d'info reccuille en OSINT")

parser.add_argument("-f","--file",type=str,default="divinatio_setting.conf",help="Fichier de configuration personnalisé (divinatio_setting.conf)")
parser.add_argument("-fs","--filesystem",type=str,default="divinatio_config.conf",help="Fichier déclarant les moules de génération de mot de passe (divinatio_config.conf)")
parser.add_argument("-e","--end",type=str,default=None,help="Nombre de mot de passe avant l'arret du script (^C si non précisé)")
parser.add_argument("-es","--endsize",type=str,default=None,help="Taille du fichier final à atteindre avant l'arrêt du script")
parser.add_argument("-o","--outfile",type=str,default="password.txt",help="Nom du fichier de sortie (word list)")
parser.add_argument("-v", "--verbosesize",nargs='?', const=True, default=False, help="Affiche la taille du fichier de sortie en temps réel")

args = parser.parse_args()

def pop_empty(ls):
	# [''] -> []
	r=[]
	for i in ls:
		if i != '':
			r.append(i)
	return r

def pop_double(ls):
	# ['a', 'a'] -> ['a']
	r=[]
	for i in ls:
		if i not in r:
			r.append(i)
	return r

def get_size(filename):
	# in Mo
	try:
		r = int(stat(filename).st_size)
		r = round(r/1024**2, 3)
	except:
		r = "None"
	return r

def get_info(conf_file):
	try:
		file = open(conf_file, "r")
		c = file.read().split("\n")
		file.close()
	except:
		exit(f"FAIL ERR: Loading divinatio_setting.conf ({conf_file})")
	try:
		#Delete commentaire:
		c2 = []
		for i in c:
			if i != '':
				t=0
				while str(i[t]) == " " or str(i[t]) == "\t": #\t = tab
					t+=1
				if str(i[t]) != "#":
					c2.append(str(i))
		c = "\n".join(c2)
	except:
		exit("FAIL ERR: Delete the # com in file",c)
	result = {
		"NAME":'',
		"LASTNAME":'',
		"OTHERNAME":'',
		"MAINPSEUDO":'',
		"OTHERPSEUDO":'',
		"DAYBIRTH":'',
		"MONTHBIRTH":'',
		"YEARBIRTH":'',
		"IMPORTANTYEARS":'',
		"YEARSINTERVALLE":'',
		"NAMEANIMAL":'',
		"CITYNAME":'',
		"CITYNUMBER":'',
		"SPECIALCHAR_BEGIN":'',
		"SPECIALCHAR_MIDDLE":'',
		"SPECIALCHAR_END":'',
		"MINLEN":'',
		"MAXLEN":''
	}
	for key in result:
		try:
			user_data=c.split(str(key) + ":")[1].split('\n')[0]
			if user_data == "":
				print("INFO: pas de donné pour",key)
		except:
			user_data=''
			print("INFO:",key, "non renseigné")
		if key in ["CITYNUMBER", "CITYNAME", "NAMEANIMAL", "OTHERPSEUDO","OTHERNAME","IMPORTANTYEARS"]:
			user_data = user_data.split(",")
			user_data = pop_empty(user_data)
		elif key == "YEARSINTERVALLE":
			try:
				r=[]
				for u in user_data.split(","):
					start, end = u.split("-")
					if int(end) - int(start) > 0:
						for i in range(int(start), int(end) + 1):
							if str(i) not in r:
								r.append(str(i))
				user_data = r
			except:
				print("MEDIUM ERR: Bad Synthax YEARSINTERVALLE", user_data)
				user_data=[]
			user_data = pop_empty(user_data)
		elif key in ["SPECIALCHAR_END", "SPECIALCHAR_BEGIN", "SPECIALCHAR_MIDDLE"]:
			user_data = pop_empty(pop_double(list(user_data)))
		result[key]=user_data
	return result

def letter_style(word, _type):
	#Type 1 : MAJ
	#Type 2 : min
	#Type 3 : First
	#Type 4 : lasT
	#Type 5 : fIRST
	#Type 6 : All posibility (list)
	t=int(_type)
	if t == 1:
		r=str(word).upper()
	elif t == 2:
		r=str(word).lower()
	elif t == 3:
		r=str(word)[0].upper() + str(word)[1:].lower()
	elif t == 4:
		r=str(word)[:-1].lower() + str(word)[-1].upper()
	elif t == 5:
		r=str(word)[0].lower() + str(word)[1:].upper()
	else:
		r = []
		l = []
		for i in range(len(word)):
			l.append(0)
		if len(word) > 0:
			l[0] = -1
			for i in range(2**len(word)):
				l[0] = l[0] + 1
				for i in range(len(l)):
					if l[i] > 1:
						l[i] = 0
						l[i+1] = l[i+1] + 1
				w=""
				t=0
				for i in l:
					if i == 0:
						w += word[t].lower()
					else:
						w += word[t].upper()
					t+=1
				r.append(w)
		else:
			r = []
	return r

def name_style(name):
	#Return a ls ordered by posibility [max, min]
	"""
		1- marylene (whole)
		2- m (first letter)
		3- ma, mary, maryle (2 by 2)
		4- mama (repition 2 first) krkr / eaea -> NON
		4- mar, maryle(3 by 3)
		5- marylen (the other)

		Middle = ["ma", "mary", "maryle"] 
						0   mary
						-1  ma
						+1  maryle

	"""
	name = str(name)
	r = [name, name[0]]
	l = []
	for i in range(2,len(name),2):
		l.append(name[0:i])
	middle = int(len(l)/2)
	f=l[0:middle][::-1]
	e=l[middle:]
	for i in range(len(l)):
		if i%2==0:
			r.append(e[0])
			del e[0]
		else:
			r.append(f[0])
			del f[0]

	surnom = str(name[:2])*2
	voyelle = list("aeiouy")
	if surnom[0].lower() in voyelle and surnom[1].lower() not in voyelle:
		r.append(surnom)
	elif surnom[0].lower() not in voyelle and surnom[1].lower() in voyelle:
		r.append(surnom)

	for i in range(3,len(name),3):
		r.append(name[0:i])
	for i in range(1,len(name)):
		n=name[:i]
		if n not in r:
			r.append(n)
	return pop_double(r)

def special_style(word, special_char):
	# [ word<s1>, <s1>word, word<s2> ...]
	if type(special_char) != type([]):
		special_char = list(special_char)
	r=[]
	for c in special_char:
		r.append(f"{word}{c}")
		r.append(f"{c}{word}")
	return r


def get_config(config_file):
	#divinatio_config.conf
	try:
		file=open(str(config_file),"r")
		c=file.read().split("\n")
		file.close()
	except:
		exit("FAIL ERR: Can't find/open divinatio_config.conf (name ",config_file,")")
	try:
		result=[]
		for line in c:
			if line != '':
				if str(line)[0] not in list("#- \t\n"):
					sp = line.split(':')
					if sp[0] == "FONT_STYLE":
						result.append(["f",sp[1].split(",")])
					else:
						result.append(sp)
	except:
		exit("FAIL ERR: Can't parse the data of divinatio_setting.conf")
	
	return result


def process(dico,list_action,font_style_ls):
	# INPUT : dico, ["NAME", "LASTNAME"], ["1","2"]
	# OUTPUT : Toutes les possibilité pour NAME:LASTNAME en font style 1 et 2
	result=[]
	for key in list_action:
		r=[] #Résultat intermédiare
		if key in ["NAME","LASTNAME","MAINPSEUDO"]:
			name_style_ls = name_style(dico[key])
			#print(name_style_ls)
			for name in name_style_ls:
				for font_nb in font_style_ls:
					word = letter_style(name,int(font_nb))
					r.append(word)
		if key in ["OTHERNAME", "CITYNAME"]:
			for name in dico[key]:
				for name_style_ in name_style(name):
					for font_nb in font_style_ls:
						word = letter_style(name_style_, int(font_nb))
						r.append(word)
		if key in ["OTHERPSEUDO", "NAMEANIMAL"]:
			for pseudo in dico[key]:
				for font_nb in font_style_ls:
					word = letter_style(pseudo, int(font_nb))
					r.append(word)
		if key in ["DAYBIRTH","MONTHBIRTH"]:
			number = str(dico[key])
			r.append(number)
			if len(number) == 1:
				r.append(f"0{number}")
		if key in ["YEARBIRTH"]:
			try:
				number = str(dico[key])
				r.append(number)
				r.append(number[-2:])
			except:
				pass
		if key in ["CITYNUMBER"]:
			for number in dico[key]:
				r.append(str(number))
		if key in ["IMPORTANTYEARS","YEARSINTERVALLE"]:
			for year in dico[key]:
				r.append(str(year))
		if key in ["SPECIALCHAR_BEGIN", "SPECIALCHAR_MIDDLE", "SPECIALCHAR_END"]:
			for char in dico[key]:
				r.append(str(char))

		r = pop_empty(r)
		r = pop_double(r)
		if len(r) != 0:
			result.append(r)
	
	if len(result) == 0:
		return []

	end_ls=[]

	position=[]
	for i in range(len(result)):
		position.append(0)
	position[0]=-1
	tt=1
	for i in result:
		tt= tt * len(i)
	for i in range(tt):
		position[0]+=1
		t=0
		for i in position:
			if i >= len(result[t]):
				position[t] = 0
				position[t+1] = position[t+1] + 1
			t+=1
		word=""
		t=0
		for i in position:
			word+=result[t][i]
			t+=1
		end_ls.append(word)
	#print(len(end_ls),tt)
	end_ls = pop_empty(end_ls)
	end_ls = pop_double(end_ls)
	#print(len(end_ls))

	return end_ls

def init_save(filename):
	file=open(filename,"w")
	file.close()

def save(filename, word):
	file=open(filename,"a")
	file.write(f"{word}\n")
	file.close()

def hello_message(end):
	print("     _ _       _             _   _ ")
	print("  __| (_)_   _(_)_ __   __ _| |_(_) ___")
	print(" / _` | \\ \\ / / | '_ \\ / _` | __| |/ _ \\")
	print("| (_| | |\\ V /| | | | | (_| | |_| | (_) |")
	print(" \\__,_|_| \\_/ |_|_| |_|\\__,_|\\__|_|\\___/\n")
	try:
		nb = round(int(end) * 0.000013, 6)
		print(nb, "Mo")
	except:pass


if __name__=="__main__":
	hello_message(args.end)

	dico = get_info(str(args.file))

	try:
		out_file = str(args.outfile)
		init_save(out_file)
	except:
		exit("SLIGHT ERR: -o must be a string and a correct name")


	if args.end != None:
		try:
			end_nb = int(args.end)
			print(f"INFO: Arrêt après génération de {end_nb} mot de passe")
		except:
			exit("SLIGHT ERR: -e must be a integer")
	else:
		end_nb = None

	if args.endsize != None:
		try:
			end_size = float(args.endsize)
			print(f"INFO: Arrêt après que out_put_file >{end_size} Mo")
		except:
			exit("SLIGHT ERR: -es must be a float")
	else:
		end_size = None

	# Génération selon le fichier divinatio_config
	print("INFO: Génération selon le fichier", args.filesystem)
	conf=get_config(args.filesystem)
	font = ['1']
	result = []
	tt=0
	for form in conf:
		if end_nb != None and tt >= end_nb:
			space = " "*100
			exit(f"END{space}")
		if end_size != None:
			if int(get_size(out_file)*100) > int(end_size*100):
				space = " "*100
				exit(f"END{space}")	
		if form[0] == 'f':
			font = form[1]
		else:
			try:
				mp = process(dico, form, font)
				for i in mp:
					if i not in result:
						result.append(i)
						save(out_file,i)
						tt+=1
						if args.verbosesize or end_size != None:
							print(tt,get_size(out_file),"Mo", end='\r')
						else:
							print(tt,end="\r")
			except:
				pass
	#print(result)
	
	# Génération brute force (une fois que divinatio_config est fini)
	print("INFO: Génération Brute Force")
	l = [-1]
	char = list("azertyuuiopqsdfghjklmwxcvbnAZERTYUIOPQSDFGHJKLMWXCVBN1234567890&é\"\\'(-è_çà)=~#{[|`^ @]^}$£ê*ù%!§:/;.,?")
	while True:
		if end_nb != None and tt >= end_nb:
			space = " "*100
			exit(f"END{space}")
		l[0] = l[0] + 1
		for i in range(len(l)):
			if l[i] >= len(char):
				l[i] = 0
				try:
					l[i+1] = l[i+1] + 1
				except:
					l.append(0)
		r = ""
		for i in l:
			r += char[i]
		if r not in result:
			result.append(r)
			save(out_file,r)
			tt += 1
			print(tt,end="\r")

	process(dico,conf[1],['1','2','3'])
	
