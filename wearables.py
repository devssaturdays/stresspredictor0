import joblib
import math
import pandas as pd

rf = joblib.load("models/rf.pkl")  #Cargamos el random forest

meanVal = joblib.load("data/meanVal.pkl")  #Cargamos los valores medios
meanVal = pd.DataFrame(meanVal)
maxVal = joblib.load("data/maxVal.pkl")  #Cargamos los valores medios
maxVal = pd.DataFrame(maxVal)
minVal = joblib.load("data/minVal.pkl")  #Cargamos los valores medios
minVal = pd.DataFrame(minVal)
corr = joblib.load("data/correlations.pkl")
corr = dict(zip(meanVal.columns, corr))
val = joblib.load("data/meanVal.pkl") 
val = pd.DataFrame(val)


import streamlit as st


def stress_o_meter(level):
	return '''<style type="text/css">
			#arrow{
				position: relative;
				height: 30vh;
				width: 10vw;
				top: -6em;
			}
			#level{
				height: 5em;
				width: 15em;
			}
		</style>
		<center>
		<div>
			<img src="https://drive.google.com/uc?export=view&id=1tzzDAZxoFpzsEIWfdH6dfetcyeE0TdAV" id="level">
			<br>
			<img src="https://drive.google.com/uc?export=view&id=1XmIuIxpmMRjw3Xf6e9AqO7pgrMx274w_" id="arrow">
		</div>
		</center>

		<script type="text/javascript" src="https://code.jquery.com/jquery-3.6.0.min.js" integrity="sha256-/xUj+3OJU5yExlq6GSYGSHk7tPXikynS7ogEvDej/m4="crossorigin="anonymous"></script>

		<script type="text/javascript">
			$(document).ready(function(){
				$( "#arrow" ).animate({
	    			left: "'''+str( 2.4*(level -3) +0.2 )+'''em",
	  			}, 1500)
			})
		</script>'''


st.set_page_config(layout="wide")

st.markdown(
	'''
	<style>
		div[data-testid='stHorizontalBlock'] div[role='slider']{
			background-color : black
		}
	</style>''',unsafe_allow_html = True)



st.markdown(
	'''
	<img src = 'https://saturdays.ai/wp-content/uploads/2021/01/logo.png' style = 'height : 10vh; position : absolute; right : 0; top : 8vh; margin : 0'>
	''', 
	unsafe_allow_html=True)

st.title("Stress wearables")

def rr_to_hb(rr):
	rr = 1/rr
	rr = rr*1000*60
	return rr

left, mid, right = st.beta_columns((4,1,4))

# ATENCION el maximo y el minimo se invierten al pasar de RR a BPM
maxim = math.floor(rr_to_hb(minVal.hrv_MEAN_RR))
minim = math.floor(rr_to_hb(maxVal.hrv_MEAN_RR))

hrv_MEAN_RR = right.slider("Latidos por minuto", minim, maxim, step = 1, value = (minim + math.floor((maxim-minim)/2))   )
hrv_MEAN_RR = 1/(hrv_MEAN_RR/1000/60)


right.markdown(
	'''<center>
		<img src ='https://drive.google.com/uc?export=view&id=1cTRxZladPbJfCCZIB5BIkfkZC1w0raSe' style = 'width : 32%;'> 
		<br> Image by: <a href = 'https://search.creativecommons.org/photos/0716edd3-d6c3-43ea-a348-616a77ecacb3'>Bekathwia</a>
	</center''', 
	unsafe_allow_html=True)

sliders = []
def addSli(var, text, place = None):

	minim = float(minVal[var])
	maxim = float(maxVal[var])

	inc = 0
	while maxim - minim < 0.1:
		maxim = maxim*10
		minim = minim*10
		inc = inc+1
	if inc > 0:
		text = text+" · 10^"+str(inc)

	if place :
		sliders.append([
			var,
			place.slider(text, minim, maxim, step = (maxim-minim)/10, value = (maxim-minim)/2 + minim )
			])

	else:
		sliders.append([
			var,
			st.slider(text, minim, maxim, step = (maxim-minim)/10, value = (maxim-minim)/2 + minim )
			])

addSli("eda_MEAN", "Actividad electrodermica media", left)
left.markdown(
	'''<center>
		<img src ='https://live.staticflickr.com/7068/6949070181_592e6b60fd_b.jpg' style = 'width : 40%;'> <br> 
		Image by: <a href = 'https://search.creativecommons.org/photos/fc29cf47-bfc5-4ea4-832e-36d8c58b5de6'>Nikki Pugh</a>
	</center''', 
	unsafe_allow_html=True)


sc = ["hrv_MEAN_RR", "eda_MEAN", "baseline", "meditation", "stress", "amusement"]   #special cases

center = st.beta_columns((1,2,1))
state = center[1].selectbox("Situación actual",("Normal","Emocionado", "Estresado", "Meditando"))

with st.beta_expander("Configuración avanzada	(Permite acceder a todas las variables del modelo)"):
	col1, col2, col3 = st.beta_columns(3)
	num = len(val.columns)//3

	for i in val.columns[:num]:
		if i not in sc:
			addSli(i,i,col1)

	for i in val.columns[num : 2*(num+1)]:
		if i not in sc:
			addSli(i,i,col2)

	for i in val.columns[2*(num+1) :]:
		if i not in sc:
			addSli(i,i,col3)
			


def update():

	val.hrv_MEAN_RR = hrv_MEAN_RR

	for i in sliders:
		val[i[0]] = i[1]


	val.baseline = 1 if state == "Normal" else 0
	val.amusement = 1 if state == "Emocionado" else 0
	val.stress = 1 if state == "Estresado" else 0
	val.meditation = 1 if state == "Meditando" else 0

if st.button('Predict'):
			update()
			
			st.write('''
			## Results 🔍 
			''')
			nStress = int(rf.predict(val))
			if nStress < 3:
				st.text("Estres bajo")
			elif nStress <5:
				st.text("Nivel de estres normal")
			else:
				st.text("Nivel de estres alto, deberias relajarte")
			st.components.v1.html(stress_o_meter(nStress))
