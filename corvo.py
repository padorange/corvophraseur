#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
	Corvophraseur (nouvelle génération)
	-----------------------------
	copyright 2010-2024, Pierre-Alain Dorange
	
	Adapté en python depuis le script AppleScript CorvoX (pour Adium/Mac) de Aurelien
		http://www.adiumxtras.com/index.php?a=xtras&xtra_id=2646
	Concept original du Covorphraseur : Luc 'Skywalker' Heinrich
		Corvophraseur 2 (for MacOS 9)
		
	Le corvophraseur permet de générer des phrases aléatoires dans un domaine "linguistique".
	Initialement permet de créer des phrases a peu prêt cohérente dans un style alambiqué de type séries de Science-fiction (Star Trek).
	Mais adaptable a d'autres domaines de type technique, comme l'informatique, insultes du Capitaine Haddock... par exemple.

	Le corvophraseur fonctionne a partie d'un modèle et de descriptif de structure de phrase type.
	Chaque modèle est un fichier texte décrivant les éléments de construction.
	Le modèle de base 'space.corvo' crée des phrases de type Star Trek / Science-Fiction
	
	Le fichier texte de description liste les éléments possibles et a la fin les gabarits a utiliser.
	Pour un gabarit donné, corvophraseur remplace les éléments [*] par des éléments au hasard puisé dans les listes précédentes.

	Par exemple le gabarit :
		"Pas de panique ! [v] [n] [a] ne nous empêche pas [d] [n] [a] ni même [d] [n] [a]."
		[v] un verbe
		[d]	un verbe avec "de" devant
		[n] un nom
		[m] un nom masculin
		[f] un nom féminin
		[a]	un adjectif
	Adjectifs et noms pouvant être masculin ou féminin et recevoir ou pas des préfixes.

	Pourra donner (par exemple) :
		Pas de panique ! 
		phaser le multiplexeur temporel ne nous empêche pas de dupliquer le schisme modulaire ni même d'optimiser la bi-matiere phasique

	Necessite :
		Python 3.x

	Usage :
		python3 corvo.py
		python3 corvo.py -r10
		python3 corvo.py -dcomputer.txt

	BSD Licence
"""

__author__="Pierre-Alain Dorange (pdorange@mac.com)"
__date__="7/07/2024"
__copyright__="Copyright 2010-2024, Pierre-Alain Dorange"
__license__="BSD"
__version__="0.4a1"

__trace__=True
__longtrace__=False
default_data_file="space.txt"

corvo_tags=(	"[v]", # verbe
				"[n]", # nom
				"[a]", # adjectif
				"[d]", # verbe avec "de" avant
				"[m]", # nom masculin
				"[f]")	# nom féminin

# modules standards
import sys
import random
import getopt

# classes

class vocabulary:
	"""	classe vocabulary
		Lecture des données "data_file" : verbes, adjectifs, noms, prefix et gabarits de phrases
		et fonctions de mise en forme d'une phrase aléatoire
	"""
	def __init__(self):
		self.verb_list=[]
		self.adj_list=[]
		self.noun_list=[]
		self.prefix_list=[]
		self.gab_list=[]
		self.f_pattern=("[Verbes]","[Adjectifs]","[Noms]","[Prefix]","[Gabarits]")
	
	def read_data(self,filename):
		""" Lecture des données 
			format du fichier de description :
				[Verbes] (v) : 		verbe infinitif, prefixe (0=jamais, 1=toujours, 2=aléatoirement)
				[Adjectifs] (a) : 	adjectif masculin, adjectif féminin, prefixe (0=jamais, 1=toujours, 2=aléatoirement)
				[Noms] (n) : 		nom, genre (1=masculin, 2=féminin), prefixe (0=jamais, 1=toujours, 2=aléatoirement)
				[Prefix] (p) : 		prefix
				[Gabarits] : 		phrase pré-formatté en utilisant les tags 
									exemple : "il faut [v] le [n] [a]"
		"""
		f=open(filename,"r")
		current=""
		try:
			ln=1
			for line in f.readlines():		# lire ligne à ligne
				done=False
				s=line.strip("\n\r\t")		# couper les lignes
				if len(s)>0:
					if s.find('#')<0 :			# ignorer les lignes commentaires (contenant #)
						for p in self.f_pattern:	# recherche si entête de groupe
							if s.find(p)>=0:
								done=True
								current=p
						if not done:
							if self.f_pattern==self.f_pattern[4]:		# Gabartis (modèles de phrases)
								word_list=(s,)
							else:
								word_list=s.split(",")
							if current==self.f_pattern[0]:		# Verbes : verbe à l'infinit, prefixe (1=toujours, 2=aléatoirement, 3=jamais)
								self.verb_list.append((word_list[0].strip(" \""),int(word_list[1])))
							elif current==self.f_pattern[1]:	# Adjectifs : masculin, feminin, prefixe (1=toujours, 2=aléatoirement, 3=jamais)
								self.adj_list.append((word_list[0].strip(" \""),word_list[1].strip(" \""),int(word_list[2])))
							elif current==self.f_pattern[2]:	# Noms : nom, genre (1=masculin, 2=féminin) ,prefixe (1=toujours, 2=aléatoirement, 3=jamais)
								self.noun_list.append((word_list[0].strip(" \""),int(word_list[1].strip(" \"")),int(word_list[2])))
							elif current==self.f_pattern[3]:	# Prefixe : préfixe
								self.prefix_list.append(word_list[0].strip(" \""))
							elif current==self.f_pattern[4]:	# Gabarits
								self.gab_list.append(s.strip(" \""))
				ln=ln+1
		except:
			print("Unexpected error:",sys.exc_info())
			print("while procesing line",ln)
			raise
		finally:
			f.close()
		
		if __trace__:
			print("Fichiers de données :")
			print("*",len(self.verb_list),"verbe(s)")
			if __longtrace__:
				for w in self.verb_list:
					print("<%s>" % w[0])
				print()
			print("*",len(self.adj_list),"adjectif(s)")
			if __longtrace__:
				for w in self.adj_list:
					print("<%s> <%s>" % (w[0],w[1]))
				print()
			print("*",len(self.noun_list),"nom(s)")
			if __longtrace__:
				for w in self.noun_list:
					print("<%s>" % w[0])
				print()
			print("*",len(self.prefix_list),"prefixe(s)")
			if __longtrace__:
				for w in self.prefix_list:
					print("<%s>" % w[0])
				print()
			print("*",len(self.gab_list),"gabarit(s)")
			if __longtrace__:
				for w in self.gab_list:
					print("<%s>" % w)
				print()

	def get_gabarit(self):
		""" sélectionne un gabarit de phrase au hasard """
		i=int(len(self.gab_list)*random.random())
		if __longtrace__:
			print("Gabarit:", self.gab_list[i])
		return self.gab_list[i]

	def substitute_verb(self,prep):
		""" substitution d'un verbe dans un gabarit """
		i=int(len(self.verb_list)*random.random())
		v=self.verb_list[i][0]
		p=self.verb_list[i][1]
		if p==1:
			v="%s-%s" % (self.substitute_prefix(),v)
		elif p==2:
			if random.random()<0.2:
				v="%s-%s" % (self.substitute_prefix(),v)
		if prep:
			if self.check_voyelle(v):
				v="d'%s" % v
			else:
				v="de %s" % v
		return v
	
	def substitute_prefix(self):
		""" substitution d'un préfixe dans un gabarit """
		i=int(len(self.prefix_list)*random.random())
		return self.prefix_list[i]
	
	def substitute_adj(self,genre):
		""" substitution d'un adjectif dans un gabarit """
		i=int(len(self.adj_list)*random.random())
		g=genre-1
		if g<0 : g=0
		elif g>1 : g=1
		return self.adj_list[i][g]
	
	def substitute_noun(self,genre):
		""" substitution d'un nom dans un gabarit """
		i=int(len(self.noun_list)*random.random())
		n=self.noun_list[i][0]	# le nom
		g=self.noun_list[i][1]	# le genre
		p=self.noun_list[i][2]	# supporte un préfix ?
		withAdj=False
		
		if genre>0 and genre!=g :
			substitute_noun(genre)
		else:
			if p==1:
				n="%s-%s" % (self.substitute_prefix(),n)
			elif p==2:
				if random.random()<0.2:
					n="%s-%s" % (self.substitute_prefix(),n)
			if withAdj:
				n="%s %s" % (n,self.substitute_adj(g))
		if self.check_voyelle(n):
			n="l'%s" % n
		elif g==1:
			n="le %s" % n
		else:
			n="la %s" % n
			
		return (n,g)
	
	def check_voyelle(self,v):
		""" v est une voyelle ? : nécessite une apostrophe ? """
		s="aeiouyéh"
		return (s.find(v[0])>=0)
		
	def do_corvo(self):
		""" crée une corvo-phrase selon le gabarit """
		gabarit=self.get_gabarit()
		corvoPhrase=""
		genre=1
		for word in gabarit.split():
			if __longtrace__:
				print("Candidate",w)
			for tag in corvo_tags:
				if word.find(tag)>=0:
					replaceStr=""
					if tag==corvo_tags[0]:	# [v] : verbe
						replaceStr=self.substitute_verb(False)
					if tag==corvo_tags[3]:	# [d] verbe avec 'de' devant
						replaceStr=self.substitute_verb(True)
					if tag==corvo_tags[2]:	# [a] : adjectif
						replaceStr=self.substitute_adj(genre)
					if tag==corvo_tags[1]:	# [n] : nom
						(replaceStr,genre)=self.substitute_noun(0)
					if tag==corvo_tags[4]:	# [m] : nom masculin
						(replaceStr,genre)=self.substitute_noun(1)
					if tag==corvo_tags[5]:	# [f] : nom féminin
						(replaceStr,genre)=self.substitute_noun(2)
					word=replaceStr
					if __longtrace__:
						print("Candidate",word,">",replaceStr)
			if len(corvoPhrase)==0:
				corvoPhrase=word
			else:
				corvoPhrase=" ".join((corvoPhrase,word))
		if __trace__:
			print(gabarit)
		return corvoPhrase
		
	def usage(self):
		print()
		print("%s usage" % __file__)
		print("\t-h (--help) : aide")
		print("\t-d (--data) : sélectionne un fichier modèle alternatif (corvo.txt par défaut)")
		print("\t-r (--repeat) : créer plusieurs phrases (n)")

# programme principal

def main(argv):
	print("Corvophraseur (Nouvelle Génération)",__version__)
	print("-----------------------------------------------------------")
	
	data=vocabulary()	# initialiser la classe principale
	
	try: # charger les paramètres de la ligne de commande
		opts,args=getopt.getopt(argv,"hdr:",["help","data=","repeat="])
	except:
		data.usage()
		sys.exit(2)

	data_file=default_data_file
	n=1
	for opt,arg in opts:
		if opt in ("-h","--help"):
			data.usage()
		elif opt in ("-d","--data"):
			data_file=arg
		elif opt in ("-r","--repeat"):
			n=int(arg)

	# charger le fichier de données (vocabulaire)
	data.read_data(data_file)
	
	# créer une corvo-phrase
	for i in range(n):
		p=data.do_corvo()
		print(p)
		print()

if __name__=="__main__":
	main(sys.argv[1:])
