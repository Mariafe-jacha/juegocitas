# -*- coding: utf-8 -*-
"""datoss

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1zXg68qPzVb79meGlEJENcnAZwBlw-CsY
"""

import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import datetime

# -----------------------------
# Inicializar Firebase
# -----------------------------
cred = credentials.Certificate("firebase_credentials.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()

# -----------------------------
# Funciones para Firebase
# -----------------------------
def guardar_usuario(usuario):
    db.collection("usuarios").document(usuario["email"]).set(usuario)

def guardar_match(email1, email2):
    match_data = {
        "user1_email": email1,
        "user2_email": email2,
        "timestamp": datetime.datetime.now()
    }
    db.collection("matches").add(match_data)

def usuario_ya_tiene_match(email):
    matches1 = db.collection("matches").where("user1_email", "==", email).stream()
    matches2 = db.collection("matches").where("user2_email", "==", email).stream()
    return any(matches1) or any(matches2)

def signos_compatibles(signo1, signo2):
    compatibilidad = {
        "Aries": ["Leo", "Sagitario", "Géminis", "Acuario"],
        "Tauro": ["Virgo", "Capricornio", "Cáncer", "Piscis"],
        "Géminis": ["Libra", "Acuario", "Aries", "Leo"],
        "Cáncer": ["Escorpio", "Piscis", "Tauro", "Virgo"],
        "Leo": ["Aries", "Sagitario", "Géminis", "Libra"],
        "Virgo": ["Tauro", "Capricornio", "Cáncer", "Escorpio"],
        "Libra": ["Géminis", "Acuario", "Leo", "Sagitario"],
        "Escorpio": ["Cáncer", "Piscis", "Virgo", "Capricornio"],
        "Sagitario": ["Aries", "Leo", "Libra", "Acuario"],
        "Capricornio": ["Tauro", "Virgo", "Escorpio", "Piscis"],
        "Acuario": ["Géminis", "Libra", "Aries", "Sagitario"],
        "Piscis": ["Cáncer", "Escorpio", "Tauro", "Capricornio"]
    }
    return signo2 in compatibilidad.get(signo1, [])

def buscar_match(usuario):
    usuarios = db.collection("usuarios").stream()
    for doc in usuarios:
        persona = doc.to_dict()

        if persona["email"] == usuario["email"]:
            continue

        if usuario_ya_tiene_match(usuario["email"]) or usuario_ya_tiene_match(persona["email"]):
            continue

        if persona["interes_en_genero"] not in [usuario["genero"], "ambos"]:
            continue
        if usuario["interes_en_genero"] not in [persona["genero"], "ambos"]:
            continue
        if persona["tipo_relacion"] != usuario["tipo_relacion"]:
            continue
        if persona["creencia"] != usuario["creencia"]:
            continue
        if persona["quiere_hijos"] != usuario["quiere_hijos"]:
            continue
        if not signos_compatibles(usuario["signo"], persona["signo"]):
            continue

        hobbies1 = set(usuario["hobbies"])
        hobbies2 = set(persona["hobbies"])
        if len(hobbies1.intersection(hobbies2)) == 0:
            continue

        altura_ok = (
            usuario["rango_altura"] == "misma talla" or
            (usuario["rango_altura"] == "más alta" and persona["altura"] > usuario["altura"]) or
            (usuario["rango_altura"] == "más baja" and persona["altura"] < usuario["altura"])
        )

        edad_ok = (
            usuario["rango_edad"] == "misma edad" or
            (usuario["rango_edad"] == "cinco años más" and persona["edad"] <= usuario["edad"] + 5) or
            (usuario["rango_edad"] == "cinco años menos" and persona["edad"] >= usuario["edad"] - 5)
        )

        if altura_ok and edad_ok:
            return persona

    return None

# -----------------------------
# Interfaz con Streamlit
# -----------------------------
st.set_page_config(page_title="App de Citas 🔥", page_icon="❤️")
st.title("💘 Juego de Match por Afinidad")

st.markdown("Completa el formulario para buscar a alguien compatible contigo.")

with st.form("formulario"):
    nombre = st.text_input("Nombre completo")
    edad = st.number_input("Edad", min_value=18, max_value=100)
    genero = st.selectbox("Género", ["femenino", "masculino", "no binario"])
    email = st.text_input("Correo electrónico")
    universidad = st.text_input("Universidad")
    cumpleaños = st.date_input("Fecha de cumpleaños")
    tipo_relacion = st.radio("¿Qué tipo de relación buscas?", ["seria", "casual"])
    creencia = st.radio("¿Cuál es tu creencia?", ["creyente", "ateo", "agnóstico"])
    signo = st.selectbox("Signo zodiacal", ["Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo",
                                            "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis"])
    altura = st.number_input("Tu altura en metros", min_value=1.0, max_value=2.5, step=0.01)
    hobbies = st.multiselect("Selecciona tus hobbies", ["leer", "bailar", "cine", "viajar", "dibujar", "series", "deportes", "música"])
    quiere_hijos = st.radio("¿Te gustaría tener hijos?", ["sí", "no"])
    interes_en_genero = st.radio("¿En qué género estás interesado/a?", ["hombre", "mujer", "ambos"])
    rango_edad = st.radio("¿Con qué rango de edad estarías en pareja?", ["misma edad", "cinco años más", "cinco años menos"])
    rango_altura = st.radio("¿Con qué rango de altura estarías en pareja?", ["misma talla", "más alta", "más baja"])
    enviar = st.form_submit_button("Enviar y buscar pareja")

if enviar:
    usuario = {
        "nombre": nombre,
        "edad": edad,
        "genero": genero,
        "email": email,
        "universidad": universidad,
        "cumpleaños": str(cumpleaños),
        "tipo_relacion": tipo_relacion,
        "creencia": creencia,
        "signo": signo,
        "altura": altura,
        "hobbies": hobbies,
        "quiere_hijos": quiere_hijos,
        "interes_en_genero": interes_en_genero,
        "rango_edad": rango_edad,
        "rango_altura": rango_altura,
    }

    guardar_usuario(usuario)
    pareja = buscar_match(usuario)

    if pareja:
        guardar_match(usuario["email"], pareja["email"])
        st.success(f"🎉 ¡Has hecho match con {pareja['nombre']} ({pareja['email']})!")
    else:
        st.warning("😢 No encontramos una pareja compatible por ahora. ¡Intenta más tarde!")