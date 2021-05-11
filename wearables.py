import joblib
import math
import pandas as pd

dt = joblib.load("dt.pkl")  #Cargamos el arbol de decision
rf = joblib.load("rf.pkl")  #Cargamos el random forest
lr  = joblib.load("lr.pkl")  #Cargamos la linear regresion
meanVal = joblib.load("meanVal.pkl")  #Cargamos los valores medios
meanVal = pd.DataFrame(meanVal)
maxVal = joblib.load("maxVal.pkl")  #Cargamos los valores medios
maxVal = pd.DataFrame(maxVal)
minVal = joblib.load("minVal.pkl")  #Cargamos los valores medios
minVal = pd.DataFrame(minVal)
corr = joblib.load("correlations.pkl")
corr = dict(zip(meanVal.columns, corr))
val = joblib.load("meanVal.pkl") 
val = pd.DataFrame(val)


import streamlit as st 


def rr_to_hb(rr):
	rr = 1/rr
	rr = rr*1000*60
	return rr

st.write("Stress Wearables")
hrv_MEAN_RR = st.slider("Latidos por minuto", math.floor(rr_to_hb(minVal.hrv_MEAN_RR)), math.floor(rr_to_hb (maxVal.hrv_MEAN_RR)) + 1, step = 1)
hrv_MEAN_RR = 1/(hrv_MEAN_RR/1000/60)

sliders = []
def addSli(var, text):
	sliders.append([
		var,
		st.slider(text, math.floor(minVal[var]) + 0.0, math.floor(maxVal[var]) + 1.0, step = math.floor(maxVal[var]-minVal[var])/10 )
		])

addSli("hrv_KURT", "Curtosis en la activdad cardiaca")

addSli("eda_MEAN", "Actividad electrodermica")

addSli("eda_KURT", "Curtosis en la actividad electrodermica")


state = st.selectbox("Situación actual",("Normal","Emocionado", "Estresado", "Meditando"))


def update():

	val.hrv_MEAN_RR = hrv_MEAN_RR

	for i in sliders:
		val[i[0]] = i[1]

		for col in range(len(val.columns)):
			if(corr[i[0]][col] != 1):
				val[val.columns[col]] = val[val.columns[col]] + ((i[1]-meanVal[i[0]])*corr[i[0]][col])
				if val[val.columns[col]][0] > maxVal[maxVal.columns[col]][0]:
					val[val.columns[col]] = maxVal[maxVal.columns[col]]
				elif val[val.columns[col]][0]< minVal[minVal.columns[col]][0]:
					val[val.columns[col]] = minVal[minVal.columns[col]]

	for i in sliders:
		val[i[0]] = i[1]

	st.write(val)

	for i in sliders:
		val[i[0]] = i[1]


	val.baseline = 1 if state == "Normal" else 0
	val.amusement = 1 if state == "Emocionado" else 0
	val.stress = 1 if state == "Estresado" else 0
	val.meditation = 1 if state == "Meditando" else 0


if st.button('Predict'):
			update()
			
			prediction = dt.predict(val)
			st.write('''
			## Results 🔍 
			''')
			st.text(f"De acuerdo a nuestro mejor modelo, un random forest el nivel de estres es: {int(rf.predict(val))}")
			st.text(f"Otros modelos sujieren: {int(dt.predict(val))} y {int(lr.predict(val))}")
