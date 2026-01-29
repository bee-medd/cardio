import os
import random
import json
from flask import Flask, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuration de la base de données
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'cardio.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Interne(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

with app.app_context():
    db.create_all()

PERIODS = [
    {"d": "01/02 — 10/02", "r": ""},
    {"d": "11/02 — 20/02", "r": ""},
    {"d": "21/02 — 02/03", "r": "DÉBUT RAMADAN"},
    {"d": "03/03 — 12/03", "r": "RAMADAN"},
    {"d": "13/03 — 22/03", "r": "AÏD / FIN RAMADAN"},
    {"d": "23/03 — 01/04", "r": ""},
    {"d": "02/04 — 11/04", "r": ""}
]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cardio | Tirage Certifié</title>
    <style>
        body { font-family: 'Courier New', Courier, monospace; background: #e5e5e5; display: flex; justify-content: center; padding: 15px; color: #1a1a1a; }
        .container { background: white; width: 100%; max-width: 450px; padding: 25px; border: 1px solid #000; box-shadow: 10px 10px 0px rgba(0,0,0,0.1); position: relative; }
        h1 { text-align: center; font-size: 18px; text-transform: uppercase; border-bottom: 2px solid #000; padding-bottom: 10px; }
        .counter { text-align: center; font-size: 12px; margin: 15px 0; font-weight: bold; }
        input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #000; box-sizing: border-box; font-family: inherit; }
        .btn { width: 100%; padding: 15px; border: none; cursor: pointer; font-weight: bold; font-family: inherit; text-transform: uppercase; display: block; text-align: center; text-decoration: none; margin-top: 10px; }
        .btn-black { background: #000; color: white; }
        .btn-green { background: #27ae60; color: white; }
        
        /* Zone d'anarchie visuelle */
        #anarchyZone { display: none; height: 100px; border: 2px dashed #000; margin: 20px 0; align-items: center; justify-content: center; background: #ffffd0; overflow: hidden; }
        #ticker { font-size: 24px; font-weight: bold; text-align: center; }

        .list { margin-top: 20px; font-size: 13px; }
        .item { border-bottom: 1px solid #eee; padding: 5px 0; }
        
        table { width: 100%; border-collapse: collapse; margin-top: 20px; display: none; }
        th, td { border: 1px solid #000; padding: 10px; text-align: left; font-size: 11px; }
        th { background: #f2f2f2; }
        .tag { color: red; font-size: 9px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Protocole Cardiologie</h1>
        
        {% if page == 'index' %}
            <div class="counter">INSCRIPTIONS : {{ count }} / 13</div>
            
            {% if count < 13 %}
            <form action="/add" method="post">
                <input type="text" name="name" placeholder="NOM DE L'INTERNE..." required>
                <button type="submit" class="btn btn-black">S'INSCRIRE</button>
            </form>
            {% else %}
            <button class="btn btn-green" id="startBtn" onclick="runAnarchy()">LANCER LE TIRAGE CERTIFIÉ</button>
            {% endif %}

            <div id="anarchyZone">
                <div id="ticker">MÉLANGE...</div>
            </div>

            <table id="resultTable">
                <thead><tr><th>PÉRIODE</th><th>AFFECTATION</th></tr></thead>
                <tbody id="tableBody"></tbody>
            </table>

            <div class="list" id="registerList">
                <strong>REGISTRE ACTUEL :</strong>
                {% for i in internes %}
                <div class="item">{{ loop.index }}. DR. {{ i.name }}</div>
                {% endfor %}
            </div>
            
            <div style="margin-top:30px; text-align:center;">
                <a href="/reset" onclick="return confirm('Reset ?')" style="font-size:9px; color:#999;">VIDER LE REGISTRE</a>
            </div>

            <script>
                // Données passées du Python au JavaScript
                const allNames = {{ names_json|safe }};
                const periods = {{ periods_json|safe }};

                async function runAnarchy() {
                    document.getElementById('startBtn').style.display = 'none';
                    document.getElementById('registerList').style.display = 'none';
                    const zone = document.getElementById('anarchyZone');
                    const ticker = document.getElementById('ticker');
                    const table = document.getElementById('resultTable');
                    const tbody = document.getElementById('tableBody');

                    zone.style.display = 'flex';

                    // 1. PHASE D'ANARCHIE (Mélange visuel)
                    let namesForShuffle = [...allNames];
                    for (let i = 0; i < 40; i++) {
                        ticker.innerText = namesForShuffle[Math.floor(Math.random() * namesForShuffle.length)];
                        ticker.style.transform = "scale(" + (1 + Math.random()) + ")";
                        await new Promise(r => setTimeout(r, 60));
                    }

                    zone.style.display = 'none';
                    table.style.display = 'table';

                    // 2. TIRAGE RÉEL (Calculé ici pour la transparence)
                    let pool = [...allNames].sort(() => Math.random() - 0.5);

                    for (let p of periods) {
                        const d1 = pool.pop() || "---";
                        const d2 = pool.pop() || "---";
                        
                        let row = tbody.insertRow();
                        row.innerHTML = `<td>${p.d}<br><span class="tag">${p.r}</span></td><td>DR. ${d1}<br>DR. ${d2}</td>`;
                        
                        // Petit effet sonore visuel : apparition ligne par ligne
                        await new Promise(r => setTimeout(r, 400));
                    }
                }
            </script>

        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    internes = Interne.query.all()
    names = [i.name for i in internes]
    return render_template_string(
        HTML_TEMPLATE, 
        page='index', 
        internes=internes, 
        count=len(internes),
        names_json=json.dumps(names), # On envoie les noms au JS
        periods_json=json.dumps(PERIODS) # On envoie les périodes au JS
    )

@app.route('/add', methods=['POST'])
def add():
    name = request.form.get('name').strip().upper()
    if name and Interne.query.count() < 13:
        try:
            db.session.add(Interne(name=name))
            db.session.commit()
        except:
            db.session.rollback()
    return redirect(url_for('index'))

@app.route('/reset')
def reset():
    Interne.query.delete()
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5008)
