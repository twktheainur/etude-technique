import requests
import pandas as pd

file = pd.read_excel('https://github.com/Kipre/etude-technique/blob/master/2020_export_Projet_Indexation_Automatique_Notice_accesTI_public_depuis2010_20200204.xlsx?raw=true')

for i, pdf in file['ACCES_TEXTE_INTEGRAL'].iteritems():
	r = requests.get(pdf)
	r = requests.post('http://159.31.63.91:8070/api/processHeaderDocument', files={'input': r.content})
	if i == 0:
		break

print(r.text)