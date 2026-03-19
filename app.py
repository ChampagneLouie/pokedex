from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

POKEAPI = "https://pokeapi.co/api/v2"

def get_pokemon_data(name):
    resp = requests.get(f"{POKEAPI}/pokemon/{name.lower()}", timeout=5)
    if resp.status_code != 200:
        return None
    data  = resp.json()
    stats = {s["stat"]["name"]: s["base_stat"] for s in data["stats"]}
    return {
        "name":    data["name"].capitalize(),
        "id":      data["id"],
        "types":   [t["type"]["name"].capitalize() for t in data["types"]],
        "sprite":  data["sprites"]["front_default"],
        "sprite_shiny": data["sprites"]["front_shiny"],
        "hp":      stats.get("hp", 0),
        "attack":  stats.get("attack", 0),
        "defense": stats.get("defense", 0),
        "speed":   stats.get("speed", 0),
        "sp_atk":  stats.get("special-attack", 0),
        "sp_def":  stats.get("special-defense", 0),
    }

@app.route("/")
def index():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Pokedex API</title>
<link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Rajdhani:wght@400;600;700&display=swap" rel="stylesheet"/>
<style>
  :root {
    --red:    #e3350d;
    --dark:   #1a0a00;
    --gold:   #ffd700;
    --card:   rgba(255,255,255,0.04);
    --border: rgba(255,215,0,0.15);
  }
  * { margin:0; padding:0; box-sizing:border-box; }

  body {
    background: var(--dark);
    background-image:
      radial-gradient(ellipse at 20% 50%, rgba(227,53,13,0.08) 0%, transparent 60%),
      radial-gradient(ellipse at 80% 20%, rgba(255,215,0,0.05) 0%, transparent 50%);
    min-height: 100vh;
    font-family: 'Rajdhani', sans-serif;
    color: white;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 40px 20px;
  }

  /* Header */
  .header {
    text-align: center;
    margin-bottom: 50px;
    animation: fadeDown 0.6s ease;
  }
  .header h1 {
    font-family: 'Press Start 2P', monospace;
    font-size: clamp(1rem, 3vw, 1.6rem);
    color: var(--red);
    text-shadow: 0 0 30px rgba(227,53,13,0.6), 3px 3px 0 rgba(0,0,0,0.5);
    letter-spacing: 2px;
    margin-bottom: 12px;
  }
  .header p {
    color: rgba(255,255,255,0.4);
    font-size: 1em;
    letter-spacing: 3px;
    text-transform: uppercase;
  }

  /* Search */
  .search-wrap {
    display: flex;
    gap: 12px;
    margin-bottom: 50px;
    width: 100%;
    max-width: 520px;
    animation: fadeUp 0.6s ease 0.1s both;
  }
  input {
    flex: 1;
    background: rgba(255,255,255,0.06);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 14px 20px;
    color: white;
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.1em;
    font-weight: 600;
    letter-spacing: 1px;
    outline: none;
    transition: border 0.2s, background 0.2s;
  }
  input:focus {
    border-color: rgba(255,215,0,0.5);
    background: rgba(255,255,255,0.09);
  }
  input::placeholder { color: rgba(255,255,255,0.25); }
  button {
    background: var(--red);
    border: none;
    border-radius: 8px;
    padding: 14px 28px;
    color: white;
    font-family: 'Press Start 2P', monospace;
    font-size: 0.55em;
    cursor: pointer;
    transition: transform 0.15s, box-shadow 0.15s;
    box-shadow: 0 4px 15px rgba(227,53,13,0.4);
  }
  button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 25px rgba(227,53,13,0.6);
  }
  button:active { transform: translateY(0); }

  /* Card */
  .card {
    width: 100%;
    max-width: 520px;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 36px;
    display: none;
    animation: fadeUp 0.4s ease;
    backdrop-filter: blur(10px);
  }
  .card.visible { display: block; }

  .pokemon-header {
    display: flex;
    align-items: center;
    gap: 24px;
    margin-bottom: 28px;
  }
  .sprite-wrap {
    position: relative;
    flex-shrink: 0;
  }
  .sprite-wrap img {
    width: 110px;
    height: 110px;
    image-rendering: pixelated;
    filter: drop-shadow(0 0 20px rgba(255,215,0,0.25));
    cursor: pointer;
    transition: transform 0.3s;
  }
  .sprite-wrap img:hover { transform: scale(1.1) rotate(-3deg); }
  .sprite-hint {
    font-size: 0.65em;
    color: rgba(255,255,255,0.3);
    text-align: center;
    margin-top: 4px;
    letter-spacing: 1px;
  }

  .pokemon-info { flex: 1; }
  .pokemon-number {
    font-family: 'Press Start 2P', monospace;
    font-size: 0.6em;
    color: rgba(255,215,0,0.4);
    margin-bottom: 6px;
  }
  .pokemon-name {
    font-family: 'Press Start 2P', monospace;
    font-size: clamp(0.8em, 2.5vw, 1.1em);
    color: var(--gold);
    text-shadow: 0 0 20px rgba(255,215,0,0.4);
    margin-bottom: 12px;
  }
  .types { display: flex; gap: 8px; flex-wrap: wrap; }
  .type-badge {
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.8em;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
  }

  /* Type colors */
  .type-Fire     { background: #e84e0f; }
  .type-Water    { background: #1976d2; }
  .type-Grass    { background: #388e3c; }
  .type-Electric { background: #f9a825; color: #000; }
  .type-Psychic  { background: #c2185b; }
  .type-Ice      { background: #00acc1; }
  .type-Dragon   { background: #4527a0; }
  .type-Dark     { background: #37474f; }
  .type-Fairy    { background: #e91e63; }
  .type-Normal   { background: #757575; }
  .type-Fighting { background: #bf360c; }
  .type-Flying   { background: #1565c0; }
  .type-Poison   { background: #6a1b9a; }
  .type-Ground   { background: #6d4c41; }
  .type-Rock     { background: #546e7a; }
  .type-Bug      { background: #558b2f; }
  .type-Ghost    { background: #4a148c; }
  .type-Steel    { background: #455a64; }

  /* Stats */
  .stats-title {
    font-family: 'Press Start 2P', monospace;
    font-size: 0.55em;
    color: rgba(255,255,255,0.35);
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 16px;
  }
  .stat-row {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 10px;
  }
  .stat-label {
    width: 70px;
    font-size: 0.85em;
    font-weight: 700;
    color: rgba(255,255,255,0.5);
    letter-spacing: 1px;
    text-transform: uppercase;
    flex-shrink: 0;
  }
  .stat-bar-wrap {
    flex: 1;
    background: rgba(255,255,255,0.06);
    border-radius: 4px;
    height: 8px;
    overflow: hidden;
  }
  .stat-bar {
    height: 100%;
    border-radius: 4px;
    transition: width 0.8s cubic-bezier(0.22, 1, 0.36, 1);
  }
  .stat-value {
    width: 32px;
    text-align: right;
    font-weight: 700;
    font-size: 0.95em;
    color: var(--gold);
    flex-shrink: 0;
  }

  /* Divider */
  .divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 24px 0;
  }

  /* Error / Loading */
  .message {
    text-align: center;
    padding: 20px;
    font-size: 1em;
    color: rgba(255,255,255,0.5);
    letter-spacing: 2px;
  }
  .error { color: var(--red) !important; }

  /* API box */
  .api-box {
    width: 100%;
    max-width: 520px;
    margin-top: 40px;
    background: rgba(0,0,0,0.3);
    border: 1px solid rgba(255,215,0,0.1);
    border-radius: 10px;
    padding: 20px 24px;
    animation: fadeUp 0.6s ease 0.2s both;
  }
  .api-box .api-title {
    font-family: 'Press Start 2P', monospace;
    font-size: 0.5em;
    color: rgba(255,215,0,0.4);
    letter-spacing: 3px;
    margin-bottom: 14px;
  }
  .endpoint {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 10px;
    font-size: 0.9em;
  }
  .method {
    background: var(--red);
    padding: 2px 8px;
    border-radius: 4px;
    font-weight: 700;
    font-size: 0.8em;
    letter-spacing: 1px;
    flex-shrink: 0;
  }
  .endpoint code {
    color: rgba(255,255,255,0.6);
    font-family: monospace;
    font-size: 0.95em;
  }
  .endpoint code span { color: var(--gold); }

  @keyframes fadeDown {
    from { opacity:0; transform:translateY(-20px); }
    to   { opacity:1; transform:translateY(0); }
  }
  @keyframes fadeUp {
    from { opacity:0; transform:translateY(20px); }
    to   { opacity:1; transform:translateY(0); }
  }
</style>
</head>
<body>

<div class="header">
  <h1>POKEDEX API</h1>
  <p>Built by Louis · Powered by PokéAPI</p>
</div>

<div class="search-wrap">
  <input id="search" type="text" placeholder="Enter a Pokemon name..." onkeydown="if(event.key==='Enter')lookup()"/>
  <button onclick="lookup()">GO</button>
  <button onclick="random()" style="background:rgba(255,255,255,0.08);border:1px solid rgba(255,215,0,0.2);box-shadow:none;">🎲</button>
  <button onclick="compare()" style="background:rgba(255,255,255,0.08);border:1px solid rgba(255,215,0,0.2);box-shadow:none;font-family:'Rajdhani',sans-serif;font-size:0.9em;letter-spacing:1px;">VS</button>
</div>

<div class="card" id="card">
  <div id="content"></div>
</div>

<div class="api-box">
  <div class="api-title">Live Endpoints</div>
  <div class="endpoint">
    <span class="method">GET</span>
    <code>/api/pokemon/<span>{name}</span></code>
  </div>
  <div class="endpoint">
    <span class="method">GET</span>
    <code>/api/compare/<span>{p1}</span>/<span>{p2}</span></code>
  </div>
  <div class="endpoint">
    <span class="method">GET</span>
    <code>/api/random</code>
  </div>
</div>

<script>
  const STAT_COLORS = {
    hp:      '#e84e0f',
    attack:  '#f9a825',
    defense: '#1976d2',
    speed:   '#388e3c',
    sp_atk:  '#c2185b',
    sp_def:  '#4527a0',
  };
  const STAT_LABELS = {
    hp:'HP', attack:'ATK', defense:'DEF',
    speed:'SPD', sp_atk:'SP.ATK', sp_def:'SP.DEF'
  };

  let showingShiny = false;

  async function lookup() {
    const name = document.getElementById('search').value.trim();
    if (!name) return;
    showingShiny = false;
    const card    = document.getElementById('card');
    const content = document.getElementById('content');
    card.classList.add('visible');
    content.innerHTML = '<div class="message">Loading...</div>';
    try {
      const res  = await fetch(`/api/pokemon/${name}`);
      const data = await res.json();
      if (data.error) {
        content.innerHTML = `<div class="message error">❌ "${name}" not found!</div>`;
        return;
      }
      renderPokemon(data);
    } catch(e) {
      content.innerHTML = '<div class="message error">Connection error.</div>';
    }
  }

  function renderPokemon(p) {
    const types = p.types.map(t =>
      `<span class="type-badge type-${t}">${t}</span>`
    ).join('');

    const stats = ['hp','attack','defense','sp_atk','sp_def','speed'].map(key => {
      const val = p[key];
      const pct = Math.min(100, Math.round(val / 255 * 100));
      return `
        <div class="stat-row">
          <div class="stat-label">${STAT_LABELS[key]}</div>
          <div class="stat-bar-wrap">
            <div class="stat-bar" style="width:0%;background:${STAT_COLORS[key]}"
                 data-target="${pct}"></div>
          </div>
          <div class="stat-value">${val}</div>
        </div>`;
    }).join('');

    document.getElementById('content').innerHTML = `
      <div class="pokemon-header">
        <div class="sprite-wrap">
          <img id="sprite" src="${p.sprite}" alt="${p.name}" onclick="toggleShiny('${p.sprite}','${p.sprite_shiny}')"/>
          <div class="sprite-hint">click to shiny ✨</div>
        </div>
        <div class="pokemon-info">
          <div class="pokemon-number">#${String(p.id).padStart(3,'0')}</div>
          <div class="pokemon-name">${p.name}</div>
          <div class="types">${types}</div>
        </div>
      </div>
      <hr class="divider"/>
      <div class="stats-title">Base Stats</div>
      ${stats}
    `;

    // Animate bars
    requestAnimationFrame(() => {
      document.querySelectorAll('.stat-bar').forEach(bar => {
        bar.style.width = bar.dataset.target + '%';
      });
    });
  }

  function toggleShiny(normal, shiny) {
    const img = document.getElementById('sprite');
    showingShiny = !showingShiny;
    img.src = showingShiny ? shiny : normal;
  }
</script>
</body>
</html>
"""

@app.route("/api/pokemon/<name>")
def api_pokemon(name):
    data = get_pokemon_data(name)
    if not data:
        return jsonify({"error": f"{name} not found"}), 404
    return jsonify(data)

@app.route("/api/compare/<p1>/<p2>")
def api_compare(p1, p2):
    d1 = get_pokemon_data(p1)
    d2 = get_pokemon_data(p2)
    if not d1 or not d2:
        return jsonify({"error": "One or both Pokemon not found"}), 404
    return jsonify({"pokemon1": d1, "pokemon2": d2})

@app.route("/api/random")
def api_random():
    import random
    pid  = random.randint(1, 151)
    data = get_pokemon_data(str(pid))
    return jsonify(data)

from flask import Flask, jsonify, request, session
import requests
import random

app = Flask(__name__)
app.secret_key = "pokebattle2026"

POKEAPI = "https://pokeapi.co/api/v2"

def get_pokemon_data(name):
    resp = requests.get(f"{POKEAPI}/pokemon/{name.lower()}", timeout=5)
    if resp.status_code != 200:
        return None
    data  = resp.json()
    stats = {s["stat"]["name"]: s["base_stat"] for s in data["stats"]}
    return {
        "name":         data["name"].capitalize(),
        "id":           data["id"],
        "types":        [t["type"]["name"].capitalize() for t in data["types"]],
        "sprite":       data["sprites"]["front_default"],
        "sprite_shiny": data["sprites"]["front_shiny"],
        "hp":           stats.get("hp", 0),
        "attack":       stats.get("attack", 0),
        "defense":      stats.get("defense", 0),
        "speed":        stats.get("speed", 0),
        "sp_atk":       stats.get("special-attack", 0),
        "sp_def":       stats.get("special-defense", 0),
    }

def get_moves(pokemon_name, level=50):
    try:
        resp = requests.get(f"{POKEAPI}/pokemon/{pokemon_name.lower()}", timeout=5)
        if resp.status_code != 200:
            return []
        data     = resp.json()
        seen     = set()
        learnable = []
        for move_entry in data.get("moves", []):
            url = move_entry["move"]["url"]
            if url in seen:
                continue
            for v in move_entry.get("version_group_details", []):
                if v.get("move_learn_method", {}).get("name") == "level-up":
                    learn_at = v.get("level_learned_at", 0)
                    if learn_at <= level:
                        learnable.append((learn_at, url))
                        seen.add(url)
                        break
        learnable.sort(key=lambda x: x[0], reverse=True)
        moves      = []
        seen_names = set()
        for _, url in learnable[:12]:
            if len(moves) >= 4:
                break
            try:
                m     = requests.get(url, timeout=5).json()
                name  = m["name"].replace("-", " ").title()
                if name in seen_names:
                    continue
                seen_names.add(name)
                moves.append({
                    "name":     name,
                    "power":    m.get("power") or 0,
                    "accuracy": m.get("accuracy") or 100,
                    "type":     m.get("type", {}).get("name", "normal").capitalize(),
                    "category": m.get("damage_class", {}).get("name", "physical"),
                })
            except:
                continue
        if not moves:
            moves = [{"name":"Tackle","power":40,"accuracy":100,"type":"Normal","category":"physical"}]
        return moves
    except:
        return [{"name":"Tackle","power":40,"accuracy":100,"type":"Normal","category":"physical"}]

TYPE_CHART = {
    "Fire":{"Grass":2.0,"Ice":2.0,"Bug":2.0,"Steel":2.0,"Water":0.5,"Rock":0.5,"Fire":0.5,"Dragon":0.5},
    "Water":{"Fire":2.0,"Ground":2.0,"Rock":2.0,"Water":0.5,"Grass":0.5,"Dragon":0.5},
    "Grass":{"Water":2.0,"Ground":2.0,"Rock":2.0,"Fire":0.5,"Grass":0.5,"Poison":0.5,"Flying":0.5,"Bug":0.5,"Dragon":0.5},
    "Electric":{"Water":2.0,"Flying":2.0,"Electric":0.5,"Grass":0.5,"Dragon":0.5,"Ground":0.0},
    "Psychic":{"Fighting":2.0,"Poison":2.0,"Psychic":0.5,"Steel":0.5,"Dark":0.0},
    "Ice":{"Grass":2.0,"Ground":2.0,"Flying":2.0,"Dragon":2.0,"Fire":0.5,"Water":0.5,"Ice":0.5},
    "Fighting":{"Normal":2.0,"Ice":2.0,"Rock":2.0,"Dark":2.0,"Steel":2.0,"Poison":0.5,"Bug":0.5,"Psychic":0.5,"Flying":0.5,"Ghost":0.0},
    "Poison":{"Grass":2.0,"Fairy":2.0,"Poison":0.5,"Ground":0.5,"Rock":0.5,"Ghost":0.5,"Steel":0.0},
    "Ground":{"Fire":2.0,"Electric":2.0,"Poison":2.0,"Rock":2.0,"Steel":2.0,"Grass":0.5,"Bug":0.5,"Flying":0.0},
    "Flying":{"Grass":2.0,"Fighting":2.0,"Bug":2.0,"Electric":0.5,"Rock":0.5,"Steel":0.5},
    "Rock":{"Fire":2.0,"Ice":2.0,"Flying":2.0,"Bug":2.0,"Fighting":0.5,"Ground":0.5,"Steel":0.5},
    "Bug":{"Grass":2.0,"Psychic":2.0,"Dark":2.0,"Fire":0.5,"Fighting":0.5,"Flying":0.5,"Ghost":0.5,"Steel":0.5},
    "Ghost":{"Psychic":2.0,"Ghost":2.0,"Normal":0.0,"Dark":0.5},
    "Dragon":{"Dragon":2.0,"Steel":0.5,"Fairy":0.0},
    "Normal":{"Rock":0.5,"Steel":0.5,"Ghost":0.0},
    "Steel":{"Ice":2.0,"Rock":2.0,"Fairy":2.0,"Fire":0.5,"Water":0.5,"Electric":0.5,"Steel":0.5},
    "Dark":{"Psychic":2.0,"Ghost":2.0,"Fighting":0.5,"Dark":0.5,"Fairy":0.5},
}

TYPE_EMOJIS = {
    "Fire":"🔥","Water":"💧","Grass":"🌿","Electric":"⚡","Psychic":"🔮",
    "Ice":"❄️","Fighting":"🥊","Poison":"☠️","Ground":"🌍","Flying":"🌪️",
    "Rock":"🪨","Bug":"🐛","Ghost":"👻","Dragon":"🐉","Normal":"⚪",
    "Steel":"⚙️","Dark":"🌑","Fairy":"✨"
}

def calc_damage(move, attacker, defender):
    if move["power"] == 0:
        return 0, "status"
    chart      = TYPE_CHART.get(move["type"], {})
    multiplier = 1.0
    for t in defender["types"]:
        multiplier *= chart.get(t, 1.0)
    dmg = max(1, round(
        (attacker["attack"] / max(defender["defense"], 1)) *
        (move["power"] / 10) * multiplier *
        random.uniform(0.85, 1.15)
    ))
    effectiveness = "normal"
    if multiplier >= 2.0:   effectiveness = "super"
    elif multiplier == 0.0: effectiveness = "none"
    elif multiplier < 1.0:  effectiveness = "weak"
    return dmg, effectiveness

@app.route("/")
def index():
    return HOME_HTML

@app.route("/battle")
def battle_page():
    return BATTLE_HTML

@app.route("/api/pokemon/<name>")
def api_pokemon(name):
    data = get_pokemon_data(name)
    if not data:
        return jsonify({"error": f"{name} not found"}), 404
    return jsonify(data)

@app.route("/api/compare/<p1>/<p2>")
def api_compare(p1, p2):
    d1 = get_pokemon_data(p1)
    d2 = get_pokemon_data(p2)
    if not d1 or not d2:
        return jsonify({"error": "One or both Pokemon not found"}), 404
    return jsonify({"pokemon1": d1, "pokemon2": d2})

@app.route("/api/random")
def api_random():
    data = get_pokemon_data(str(random.randint(1, 151)))
    return jsonify(data)

@app.route("/api/battle/start", methods=["POST"])
def battle_start():
    body = request.json
    p1   = get_pokemon_data(body.get("p1", "pikachu"))
    p2   = get_pokemon_data(body.get("p2", "charmander"))
    if not p1 or not p2:
        return jsonify({"error": "Pokemon not found"}), 404
    m1 = get_moves(p1["name"])
    m2 = get_moves(p2["name"])
    state = {
        "p1":       p1, "p2": p2,
        "p1_moves": m1, "p2_moves": m2,
        "p1_hp":    p1["hp"], "p2_hp": p2["hp"],
        "log":      [f"⚔️ {p1['name']} vs {p2['name']} — Battle Start!"],
        "turn":     "p1" if p1["speed"] >= p2["speed"] else "p2",
        "over":     False, "winner": None
    }
    session["battle"] = state
    return jsonify(state)

@app.route("/api/battle/move", methods=["POST"])
def battle_move():
    state = session.get("battle")
    if not state or state["over"]:
        return jsonify({"error": "No active battle"}), 400

    body      = request.json
    move_idx  = body.get("move_idx", 0)
    log       = []

    p1     = state["p1"]
    p2     = state["p2"]
    p1_hp  = state["p1_hp"]
    p2_hp  = state["p2_hp"]
    m1     = state["p1_moves"]
    m2     = state["p2_moves"]

    # Player move
    move        = m1[move_idx]
    dmg, eff    = calc_damage(move, p1, p2)
    p2_hp       = max(0, p2_hp - dmg)
    emoji       = TYPE_EMOJIS.get(move["type"], "⚪")

    if eff == "status":
        log.append(f"{emoji} {p1['name']} used {move['name']}!")
    else:
        log.append(f"{emoji} {p1['name']} used {move['name']} for {dmg} damage!")
        if eff == "super": log.append("💥 It's super effective!!")
        if eff == "weak":  log.append("😐 It's not very effective...")
        if eff == "none":  log.append("🚫 It had no effect!")

    if p2_hp <= 0:
        log.append(f"💀 {p2['name']} fainted! {p1['name']} wins! 🏆")
        state.update({"p1_hp": p1_hp, "p2_hp": 0, "log": log, "over": True, "winner": "p1"})
        session["battle"] = state
        return jsonify(state)

    # Enemy move
    e_move      = random.choice(m2)
    e_dmg, e_eff = calc_damage(e_move, p2, p1)
    p1_hp       = max(0, p1_hp - e_dmg)
    e_emoji     = TYPE_EMOJIS.get(e_move["type"], "⚪")

    if e_eff == "status":
        log.append(f"{e_emoji} {p2['name']} used {e_move['name']}!")
    else:
        log.append(f"{e_emoji} {p2['name']} used {e_move['name']} for {e_dmg} damage!")
        if e_eff == "super": log.append("💥 It's super effective!!")
        if e_eff == "weak":  log.append("😐 It's not very effective...")

    if p1_hp <= 0:
        log.append(f"💀 {p1['name']} fainted! {p2['name']} wins! 🏆")
        state.update({"p1_hp": 0, "p2_hp": p2_hp, "log": log, "over": True, "winner": "p2"})
        session["battle"] = state
        return jsonify(state)

    log.append(f"HP: {p1['name']} {p1_hp}/{p1['hp']} | {p2['name']} {p2_hp}/{p2['hp']}")
    state.update({"p1_hp": p1_hp, "p2_hp": p2_hp, "log": log, "over": False})
    session["battle"] = state
    return jsonify(state)

HOME_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Pokedex</title>
<link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Rajdhani:wght@400;600;700&display=swap" rel="stylesheet"/>
<style>
  :root { --red:#e3350d; --dark:#1a0a00; --gold:#ffd700; --card:rgba(255,255,255,0.04); --border:rgba(255,215,0,0.15); }
  *{margin:0;padding:0;box-sizing:border-box;}
  body{background:var(--dark);background-image:radial-gradient(ellipse at 20% 50%,rgba(227,53,13,0.08) 0%,transparent 60%),radial-gradient(ellipse at 80% 20%,rgba(255,215,0,0.05) 0%,transparent 50%);min-height:100vh;font-family:'Rajdhani',sans-serif;color:white;display:flex;flex-direction:column;align-items:center;padding:40px 20px;}
  .header{text-align:center;margin-bottom:40px;animation:fadeDown 0.6s ease;}
  .header h1{font-family:'Press Start 2P',monospace;font-size:clamp(1rem,3vw,1.6rem);color:var(--red);text-shadow:0 0 30px rgba(227,53,13,0.6),3px 3px 0 rgba(0,0,0,0.5);letter-spacing:2px;margin-bottom:12px;}
  .header p{color:rgba(255,255,255,0.4);font-size:1em;letter-spacing:3px;text-transform:uppercase;}
  .nav{display:flex;gap:12px;margin-bottom:40px;}
  .nav a{background:rgba(255,255,255,0.06);border:1px solid var(--border);border-radius:8px;padding:10px 24px;color:rgba(255,255,255,0.7);text-decoration:none;font-family:'Press Start 2P',monospace;font-size:0.5em;letter-spacing:1px;transition:all 0.2s;}
  .nav a:hover,.nav a.active{background:var(--red);border-color:var(--red);color:white;box-shadow:0 4px 15px rgba(227,53,13,0.4);}
  .search-wrap{display:flex;gap:12px;margin-bottom:40px;width:100%;max-width:520px;animation:fadeUp 0.6s ease 0.1s both;}
  input{flex:1;background:rgba(255,255,255,0.06);border:1px solid var(--border);border-radius:8px;padding:14px 20px;color:white;font-family:'Rajdhani',sans-serif;font-size:1.1em;font-weight:600;letter-spacing:1px;outline:none;transition:border 0.2s,background 0.2s;}
  input:focus{border-color:rgba(255,215,0,0.5);background:rgba(255,255,255,0.09);}
  input::placeholder{color:rgba(255,255,255,0.25);}
  button{background:var(--red);border:none;border-radius:8px;padding:14px 28px;color:white;font-family:'Press Start 2P',monospace;font-size:0.55em;cursor:pointer;transition:transform 0.15s,box-shadow 0.15s;box-shadow:0 4px 15px rgba(227,53,13,0.4);}
  button:hover{transform:translateY(-2px);box-shadow:0 6px 25px rgba(227,53,13,0.6);}
  .card{width:100%;max-width:520px;background:var(--card);border:1px solid var(--border);border-radius:16px;padding:36px;display:none;animation:fadeUp 0.4s ease;backdrop-filter:blur(10px);}
  .card.visible{display:block;}
  .pokemon-header{display:flex;align-items:center;gap:24px;margin-bottom:28px;}
  .sprite-wrap{position:relative;flex-shrink:0;}
  .sprite-wrap img{width:110px;height:110px;image-rendering:pixelated;filter:drop-shadow(0 0 20px rgba(255,215,0,0.25));cursor:pointer;transition:transform 0.3s;}
  .sprite-wrap img:hover{transform:scale(1.1) rotate(-3deg);}
  .sprite-hint{font-size:0.65em;color:rgba(255,255,255,0.3);text-align:center;margin-top:4px;letter-spacing:1px;}
  .pokemon-info{flex:1;}
  .pokemon-number{font-family:'Press Start 2P',monospace;font-size:0.6em;color:rgba(255,215,0,0.4);margin-bottom:6px;}
  .pokemon-name{font-family:'Press Start 2P',monospace;font-size:clamp(0.8em,2.5vw,1.1em);color:var(--gold);text-shadow:0 0 20px rgba(255,215,0,0.4);margin-bottom:12px;}
  .types{display:flex;gap:8px;flex-wrap:wrap;}
  .type-badge{padding:4px 14px;border-radius:20px;font-size:0.8em;font-weight:700;letter-spacing:1px;text-transform:uppercase;}
  .type-Fire{background:#e84e0f;} .type-Water{background:#1976d2;} .type-Grass{background:#388e3c;} .type-Electric{background:#f9a825;color:#000;} .type-Psychic{background:#c2185b;} .type-Ice{background:#00acc1;} .type-Dragon{background:#4527a0;} .type-Dark{background:#37474f;} .type-Fairy{background:#e91e63;} .type-Normal{background:#757575;} .type-Fighting{background:#bf360c;} .type-Flying{background:#1565c0;} .type-Poison{background:#6a1b9a;} .type-Ground{background:#6d4c41;} .type-Rock{background:#546e7a;} .type-Bug{background:#558b2f;} .type-Ghost{background:#4a148c;} .type-Steel{background:#455a64;}
  .divider{border:none;border-top:1px solid var(--border);margin:24px 0;}
  .stats-title{font-family:'Press Start 2P',monospace;font-size:0.55em;color:rgba(255,255,255,0.35);letter-spacing:3px;text-transform:uppercase;margin-bottom:16px;}
  .stat-row{display:flex;align-items:center;gap:12px;margin-bottom:10px;}
  .stat-label{width:70px;font-size:0.85em;font-weight:700;color:rgba(255,255,255,0.5);letter-spacing:1px;text-transform:uppercase;flex-shrink:0;}
  .stat-bar-wrap{flex:1;background:rgba(255,255,255,0.06);border-radius:4px;height:8px;overflow:hidden;}
  .stat-bar{height:100%;border-radius:4px;transition:width 0.8s cubic-bezier(0.22,1,0.36,1);}
  .stat-value{width:32px;text-align:right;font-weight:700;font-size:0.95em;color:var(--gold);flex-shrink:0;}
  .api-box{width:100%;max-width:520px;margin-top:40px;background:rgba(0,0,0,0.3);border:1px solid rgba(255,215,0,0.1);border-radius:10px;padding:20px 24px;animation:fadeUp 0.6s ease 0.2s both;}
  .api-box .api-title{font-family:'Press Start 2P',monospace;font-size:0.5em;color:rgba(255,215,0,0.4);letter-spacing:3px;margin-bottom:14px;}
  .endpoint{display:flex;align-items:center;gap:10px;margin-bottom:10px;font-size:0.9em;}
  .method{background:var(--red);padding:2px 8px;border-radius:4px;font-weight:700;font-size:0.8em;letter-spacing:1px;flex-shrink:0;}
  .endpoint code{color:rgba(255,255,255,0.6);font-family:monospace;font-size:0.95em;}
  .endpoint code span{color:var(--gold);}
  .message{text-align:center;padding:20px;font-size:1em;color:rgba(255,255,255,0.5);letter-spacing:2px;}
  .error{color:var(--red)!important;}
  @keyframes fadeDown{from{opacity:0;transform:translateY(-20px)}to{opacity:1;transform:translateY(0)}}
  @keyframes fadeUp{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
</style>
</head>
<body>
<div class="header"><h1>POKEDEX</h1><p>Built by Louis · Powered by PokéAPI</p></div>
<div class="nav">
  <a href="/" class="active">🔍 Lookup</a>
  <a href="/battle">⚔️ Battle</a>
</div>
<div class="search-wrap">
  <input id="search" type="text" placeholder="Enter a Pokemon name..." onkeydown="if(event.key==='Enter')lookup()"/>
  <button onclick="lookup()">GO</button>
</div>
<div class="card" id="card"><div id="content"></div></div>
<div class="api-box">
  <div class="api-title">Live Endpoints</div>
  <div class="endpoint"><span class="method">GET</span><code>/api/pokemon/<span>{name}</span></code></div>
  <div class="endpoint"><span class="method">GET</span><code>/api/compare/<span>{p1}</span>/<span>{p2}</span></code></div>
  <div class="endpoint"><span class="method">GET</span><code>/api/random</code></div>
  <div class="endpoint"><span class="method">POST</span><code>/api/battle/start</code></div>
  <div class="endpoint"><span class="method">POST</span><code>/api/battle/move</code></div>
</div>
<script>
  const STAT_COLORS={hp:'#e84e0f',attack:'#f9a825',defense:'#1976d2',speed:'#388e3c',sp_atk:'#c2185b',sp_def:'#4527a0'};
  const STAT_LABELS={hp:'HP',attack:'ATK',defense:'DEF',speed:'SPD',sp_atk:'SP.ATK',sp_def:'SP.DEF'};
  let showingShiny=false;
  async function lookup(){
    const name=document.getElementById('search').value.trim();
    if(!name)return;
    showingShiny=false;
    const card=document.getElementById('card');
    const content=document.getElementById('content');
    card.classList.add('visible');
    content.innerHTML='<div class="message">Loading...</div>';
    try{
      const res=await fetch(`/api/pokemon/${name}`);
      const data=await res.json();
      if(data.error){content.innerHTML=`<div class="message error">❌ "${name}" not found!</div>`;return;}
      renderPokemon(data);
    }catch(e){content.innerHTML='<div class="message error">Connection error.</div>';}
  }
  function renderPokemon(p){
    const types=p.types.map(t=>`<span class="type-badge type-${t}">${t}</span>`).join('');
    const stats=['hp','attack','defense','sp_atk','sp_def','speed'].map(key=>{
      const val=p[key];const pct=Math.min(100,Math.round(val/255*100));
      return`<div class="stat-row"><div class="stat-label">${STAT_LABELS[key]}</div><div class="stat-bar-wrap"><div class="stat-bar" style="width:0%;background:${STAT_COLORS[key]}" data-target="${pct}"></div></div><div class="stat-value">${val}</div></div>`;
    }).join('');
    document.getElementById('content').innerHTML=`
      <div class="pokemon-header">
        <div class="sprite-wrap">
          <img id="sprite" src="${p.sprite}" alt="${p.name}" onclick="toggleShiny('${p.sprite}','${p.sprite_shiny}')"/>
          <div class="sprite-hint">click for shiny ✨</div>
        </div>
        <div class="pokemon-info">
          <div class="pokemon-number">#${String(p.id).padStart(3,'0')}</div>
          <div class="pokemon-name">${p.name}</div>
          <div class="types">${types}</div>
        </div>
      </div>
      <hr class="divider"/>
      <div class="stats-title">Base Stats</div>${stats}`;
    requestAnimationFrame(()=>{
      document.querySelectorAll('.stat-bar').forEach(b=>{b.style.width=b.dataset.target+'%';});
    });
  }
  function toggleShiny(n,s){const img=document.getElementById('sprite');showingShiny=!showingShiny;img.src=showingShiny?s:n;}
async function random() {
  document.getElementById('search').value = '';
  showingShiny = false;
  const card    = document.getElementById('card');
  const content = document.getElementById('content');
  card.classList.add('visible');
  content.innerHTML = '<div class="message">Finding a random Pokemon...</div>';
  try {
    const res  = await fetch('/api/random');
    const data = await res.json();
    document.getElementById('search').value = data.name;
    renderPokemon(data);
  } catch(e) {
    content.innerHTML = '<div class="message error">Connection error.</div>';
  }
}

async function compare() {
  const name = document.getElementById('search').value.trim();
  if (!name) { alert('Enter a Pokemon name first then click Compare!'); return; }
  const rival = prompt('Enter a Pokemon to compare against:');
  if (!rival) return;
  const card    = document.getElementById('card');
  const content = document.getElementById('content');
  card.classList.add('visible');
  content.innerHTML = '<div class="message">Loading comparison...</div>';
  try {
    const res  = await fetch(`/api/compare/${name}/${rival}`);
    const data = await res.json();
    if (data.error) { content.innerHTML = `<div class="message error">❌ ${data.error}</div>`; return; }
    renderComparison(data.pokemon1, data.pokemon2);
  } catch(e) {
    content.innerHTML = '<div class="message error">Connection error.</div>';
  }
}

function renderComparison(p1, p2) {
  const STAT_COLORS={hp:'#e84e0f',attack:'#f9a825',defense:'#1976d2',speed:'#388e3c',sp_atk:'#c2185b',sp_def:'#4527a0'};
  const STAT_LABELS={hp:'HP',attack:'ATK',defense:'DEF',speed:'SPD',sp_atk:'SP.ATK',sp_def:'SP.DEF'};

  const types1 = p1.types.map(t => `<span class="type-badge type-${t}">${t}</span>`).join('');
  const types2 = p2.types.map(t => `<span class="type-badge type-${t}">${t}</span>`).join('');

  const stats = ['hp','attack','defense','sp_atk','sp_def','speed'].map(key => {
    const v1   = p1[key];
    const v2   = p2[key];
    const pct1 = Math.min(100, Math.round(v1/255*100));
    const pct2 = Math.min(100, Math.round(v2/255*100));
    const winner = v1 > v2 ? 'p1' : v2 > v1 ? 'p2' : 'tie';
    return `
      <div style="margin-bottom:14px;">
        <div style="display:flex;justify-content:space-between;font-size:0.8em;color:rgba(255,255,255,0.4);margin-bottom:4px;">
          <span style="color:${winner==='p1'?'#ffd700':'rgba(255,255,255,0.4)'};font-weight:${winner==='p1'?'700':'400'}">${v1}</span>
          <span style="letter-spacing:2px;text-transform:uppercase;">${STAT_LABELS[key]}</span>
          <span style="color:${winner==='p2'?'#ffd700':'rgba(255,255,255,0.4)'};font-weight:${winner==='p2'?'700':'400'}">${v2}</span>
        </div>
        <div style="display:flex;gap:4px;align-items:center;">
          <div style="flex:1;background:rgba(255,255,255,0.06);border-radius:4px;height:8px;overflow:hidden;transform:scaleX(-1)">
            <div style="height:100%;width:${pct1}%;background:${STAT_COLORS[key]};border-radius:4px;transition:width 0.8s cubic-bezier(0.22,1,0.36,1);"></div>
          </div>
          <div style="flex:1;background:rgba(255,255,255,0.06);border-radius:4px;height:8px;overflow:hidden;">
            <div style="height:100%;width:${pct2}%;background:${STAT_COLORS[key]};border-radius:4px;transition:width 0.8s cubic-bezier(0.22,1,0.36,1);"></div>
          </div>
        </div>
      </div>`;
  }).join('');

  const total1 = p1.hp+p1.attack+p1.defense+p1.sp_atk+p1.sp_def+p1.speed;
  const total2 = p2.hp+p2.attack+p2.defense+p2.sp_atk+p2.sp_def+p2.speed;
  const overall = total1 > total2 ? p1.name : total2 > total1 ? p2.name : 'Tie';

  document.getElementById('content').innerHTML = `
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:24px;gap:16px;">
      <div style="text-align:center;flex:1;">
        <img src="${p1.sprite}" style="width:90px;height:90px;image-rendering:pixelated;filter:drop-shadow(0 0 15px rgba(255,215,0,0.2));"/>
        <div style="font-family:'Press Start 2P',monospace;font-size:0.55em;color:#ffd700;margin-top:6px;">${p1.name}</div>
        <div style="margin-top:6px;">${types1}</div>
      </div>
      <div style="font-family:'Press Start 2P',monospace;font-size:0.8em;color:#e3350d;text-shadow:0 0 15px rgba(227,53,13,0.6);">VS</div>
      <div style="text-align:center;flex:1;">
        <img src="${p2.sprite}" style="width:90px;height:90px;image-rendering:pixelated;filter:drop-shadow(0 0 15px rgba(255,215,0,0.2));"/>
        <div style="font-family:'Press Start 2P',monospace;font-size:0.55em;color:#ffd700;margin-top:6px;">${p2.name}</div>
        <div style="margin-top:6px;">${types2}</div>
      </div>
    </div>
    <hr class="divider"/>
    <div class="stats-title">Stat Comparison</div>
    ${stats}
    <div style="text-align:center;margin-top:16px;padding:12px;background:rgba(255,215,0,0.08);border:1px solid rgba(255,215,0,0.2);border-radius:8px;">
      <span style="font-family:'Press Start 2P',monospace;font-size:0.55em;color:#ffd700;">
        🏆 ${overall === 'Tie' ? "It's a tie!" : overall + ' wins overall!'}
      </span>
      <div style="font-size:0.8em;color:rgba(255,255,255,0.4);margin-top:6px;">${p1.name}: ${total1} pts vs ${p2.name}: ${total2} pts</div>
    </div>`;

  requestAnimationFrame(()=>{
    document.querySelectorAll('[style*="width:0%"]').forEach(b=>{
      const target = b.style.width;
      b.style.width = '0%';
      setTimeout(()=>{ b.style.width = target; }, 50);
    });
  });
}
</script>
</body></html>"""

BATTLE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Pokemon Battle</title>
<link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Rajdhani:wght@400;600;700&display=swap" rel="stylesheet"/>
<style>
  :root{--red:#e3350d;--dark:#0d0d1a;--gold:#ffd700;--green:#4caf50;--border:rgba(255,215,0,0.15);}
  *{margin:0;padding:0;box-sizing:border-box;}
  body{background:var(--dark);background-image:radial-gradient(ellipse at 30% 40%,rgba(227,53,13,0.07) 0%,transparent 60%),radial-gradient(ellipse at 70% 60%,rgba(100,100,255,0.07) 0%,transparent 60%);min-height:100vh;font-family:'Rajdhani',sans-serif;color:white;display:flex;flex-direction:column;align-items:center;padding:30px 20px;}
  .header{text-align:center;margin-bottom:30px;}
  .header h1{font-family:'Press Start 2P',monospace;font-size:clamp(0.8rem,2.5vw,1.2rem);color:var(--red);text-shadow:0 0 30px rgba(227,53,13,0.6);margin-bottom:8px;}
  .nav{display:flex;gap:12px;margin-bottom:30px;}
  .nav a{background:rgba(255,255,255,0.06);border:1px solid var(--border);border-radius:8px;padding:10px 24px;color:rgba(255,255,255,0.7);text-decoration:none;font-family:'Press Start 2P',monospace;font-size:0.5em;transition:all 0.2s;}
  .nav a:hover,.nav a.active{background:var(--red);border-color:var(--red);color:white;}

  /* Setup */
  .setup{width:100%;max-width:560px;background:rgba(255,255,255,0.03);border:1px solid var(--border);border-radius:16px;padding:30px;margin-bottom:20px;}
  .setup h2{font-family:'Press Start 2P',monospace;font-size:0.6em;color:var(--gold);letter-spacing:2px;margin-bottom:20px;text-align:center;}
  .setup-row{display:flex;gap:12px;align-items:center;margin-bottom:12px;}
  .setup-label{font-family:'Press Start 2P',monospace;font-size:0.5em;color:var(--red);width:30px;flex-shrink:0;}
  .setup input{flex:1;background:rgba(255,255,255,0.06);border:1px solid var(--border);border-radius:8px;padding:12px 16px;color:white;font-family:'Rajdhani',sans-serif;font-size:1em;font-weight:600;outline:none;transition:border 0.2s;}
  .setup input:focus{border-color:rgba(255,215,0,0.5);}
  .setup input::placeholder{color:rgba(255,255,255,0.25);}
  .start-btn{width:100%;margin-top:8px;background:var(--red);border:none;border-radius:8px;padding:14px;color:white;font-family:'Press Start 2P',monospace;font-size:0.55em;cursor:pointer;transition:transform 0.15s,box-shadow 0.15s;box-shadow:0 4px 15px rgba(227,53,13,0.4);}
  .start-btn:hover{transform:translateY(-2px);box-shadow:0 6px 25px rgba(227,53,13,0.6);}

  /* Arena */
  .arena{width:100%;max-width:700px;display:none;}
  .arena.visible{display:block;}

  /* Pokemon row */
  .fighters{display:flex;justify-content:space-between;align-items:flex-end;gap:20px;margin-bottom:24px;}
  .fighter{flex:1;background:rgba(255,255,255,0.03);border:1px solid var(--border);border-radius:14px;padding:20px;text-align:center;}
  .fighter.you{border-color:rgba(76,175,80,0.3);}
  .fighter.enemy{border-color:rgba(227,53,13,0.3);}
  .fighter-label{font-family:'Press Start 2P',monospace;font-size:0.45em;margin-bottom:10px;letter-spacing:2px;}
  .you .fighter-label{color:var(--green);}
  .enemy .fighter-label{color:var(--red);}
  .fighter img{width:90px;height:90px;image-rendering:pixelated;filter:drop-shadow(0 0 15px rgba(255,215,0,0.2));}
  .fighter-name{font-family:'Press Start 2P',monospace;font-size:0.5em;color:var(--gold);margin:8px 0 6px;}
  .hp-bar-wrap{background:rgba(255,255,255,0.08);border-radius:4px;height:10px;overflow:hidden;margin-bottom:4px;}
  .hp-bar{height:100%;border-radius:4px;transition:width 0.5s ease,background 0.3s;}
  .hp-text{font-size:0.8em;color:rgba(255,255,255,0.5);font-weight:600;}

  .vs-badge{font-family:'Press Start 2P',monospace;font-size:0.9em;color:var(--red);text-shadow:0 0 20px rgba(255,68,68,0.8);animation:pulse 1s infinite;align-self:center;flex-shrink:0;}
  @keyframes pulse{0%,100%{transform:scale(1)}50%{transform:scale(1.2)}}

  /* Battle log */
  .log-box{background:rgba(0,0,0,0.4);border:1px solid var(--border);border-radius:10px;padding:16px;height:130px;overflow-y:auto;margin-bottom:20px;font-size:0.95em;line-height:1.7;}
  .log-box p{margin:0;color:rgba(255,255,255,0.8);}
  .log-box p.highlight{color:var(--gold);font-weight:700;}
  .log-box p.red{color:var(--red);}
  .log-box p.green{color:var(--green);}

  /* Moves */
  .moves-title{font-family:'Press Start 2P',monospace;font-size:0.5em;color:rgba(255,255,255,0.3);letter-spacing:3px;margin-bottom:12px;}
  .moves-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:20px;}
  .move-btn{background:rgba(255,255,255,0.05);border:1px solid var(--border);border-radius:10px;padding:14px 16px;color:white;font-family:'Rajdhani',sans-serif;font-size:0.95em;font-weight:700;cursor:pointer;text-align:left;transition:all 0.2s;display:flex;flex-direction:column;gap:4px;}
  .move-btn:hover:not(:disabled){background:rgba(255,215,0,0.1);border-color:rgba(255,215,0,0.4);transform:translateY(-2px);}
  .move-btn:disabled{opacity:0.4;cursor:not-allowed;}
  .move-name{font-size:1em;}
  .move-meta{font-size:0.75em;color:rgba(255,255,255,0.4);letter-spacing:1px;}

  /* Result */
  .result-banner{display:none;text-align:center;padding:24px;background:rgba(255,215,0,0.08);border:1px solid rgba(255,215,0,0.3);border-radius:12px;margin-bottom:20px;}
  .result-banner.visible{display:block;animation:fadeUp 0.5s ease;}
  .result-banner h2{font-family:'Press Start 2P',monospace;font-size:0.9em;color:var(--gold);margin-bottom:12px;}
  .rematch-btn{background:var(--red);border:none;border-radius:8px;padding:12px 28px;color:white;font-family:'Press Start 2P',monospace;font-size:0.5em;cursor:pointer;transition:all 0.2s;box-shadow:0 4px 15px rgba(227,53,13,0.4);}
  .rematch-btn:hover{transform:translateY(-2px);}

  .loading{text-align:center;padding:30px;font-family:'Press Start 2P',monospace;font-size:0.6em;color:rgba(255,255,255,0.4);letter-spacing:2px;}

  @keyframes fadeUp{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
  @keyframes shake{0%,100%{transform:translateX(0)}25%{transform:translateX(-8px)}75%{transform:translateX(8px)}}
  .shake{animation:shake 0.3s ease;}
</style>
</head>
<body>
<div class="header"><h1>⚔️ POKEMON BATTLE</h1></div>
<div class="nav">
  <a href="/">🔍 Lookup</a>
  <a href="/battle" class="active">⚔️ Battle</a>
</div>

<!-- Setup -->
<div class="setup" id="setup">
  <h2>Choose Your Fighters</h2>
  <div class="setup-row">
    <div class="setup-label">P1</div>
    <input id="p1" type="text" placeholder="Your Pokemon (e.g. charizard)" value="charizard"/>
  </div>
  <div class="setup-row">
    <div class="setup-label">VS</div>
    <input id="p2" type="text" placeholder="Enemy Pokemon (e.g. blastoise)" value="blastoise"/>
  </div>
  <button class="start-btn" onclick="startBattle()">⚔️ START BATTLE</button>
</div>

<!-- Arena -->
<div class="arena" id="arena">
  <div class="fighters">
    <div class="fighter you">
      <div class="fighter-label">YOU</div>
      <img id="p1-sprite" src="" alt=""/>
      <div class="fighter-name" id="p1-name"></div>
      <div class="hp-bar-wrap"><div class="hp-bar" id="p1-bar" style="width:100%;background:#4caf50;"></div></div>
      <div class="hp-text" id="p1-hp-text"></div>
    </div>
    <div class="vs-badge">VS</div>
    <div class="fighter enemy">
      <div class="fighter-label">ENEMY</div>
      <img id="p2-sprite" src="" alt=""/>
      <div class="fighter-name" id="p2-name"></div>
      <div class="hp-bar-wrap"><div class="hp-bar" id="p2-bar" style="width:100%;background:#e3350d;"></div></div>
      <div class="hp-text" id="p2-hp-text"></div>
    </div>
  </div>

  <div class="log-box" id="log"></div>

  <div class="result-banner" id="result">
    <h2 id="result-text"></h2>
    <button class="rematch-btn" onclick="rematch()">🔄 REMATCH</button>
  </div>

  <div class="moves-title">YOUR MOVES</div>
  <div class="moves-grid" id="moves"></div>
</div>

<script>
let state = null;

const TYPE_COLORS = {
  Fire:'#e84e0f',Water:'#1976d2',Grass:'#388e3c',Electric:'#f9a825',
  Psychic:'#c2185b',Ice:'#00acc1',Dragon:'#4527a0',Dark:'#37474f',
  Fairy:'#e91e63',Normal:'#757575',Fighting:'#bf360c',Flying:'#1565c0',
  Poison:'#6a1b9a',Ground:'#6d4c41',Rock:'#546e7a',Bug:'#558b2f',
  Ghost:'#4a148c',Steel:'#455a64'
};

async function startBattle() {
  const p1 = document.getElementById('p1').value.trim();
  const p2 = document.getElementById('p2').value.trim();
  if (!p1 || !p2) return;

  document.getElementById('setup').style.display = 'none';
  document.getElementById('arena').classList.add('visible');
  document.getElementById('log').innerHTML = '<div class="loading">Loading battle data...</div>';
  document.getElementById('moves').innerHTML = '';
  document.getElementById('result').classList.remove('visible');

  const res  = await fetch('/api/battle/start', {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({p1, p2})
  });
  state = await res.json();

  if (state.error) {
    document.getElementById('log').innerHTML = `<p class="red">❌ ${state.error}</p>`;
    return;
  }

  updateUI();
  renderMoves();
}

function updateUI() {
  if (!state) return;
  const p1     = state.p1;
  const p2     = state.p2;
  const p1_pct = Math.max(0, Math.round(state.p1_hp / p1.hp * 100));
  const p2_pct = Math.max(0, Math.round(state.p2_hp / p2.hp * 100));

  document.getElementById('p1-sprite').src = p1.sprite;
  document.getElementById('p2-sprite').src = p2.sprite;
  document.getElementById('p1-name').textContent = p1.name;
  document.getElementById('p2-name').textContent = p2.name;
  document.getElementById('p1-hp-text').textContent = `${state.p1_hp} / ${p1.hp} HP`;
  document.getElementById('p2-hp-text').textContent = `${state.p2_hp} / ${p2.hp} HP`;

  const p1Bar = document.getElementById('p1-bar');
  const p2Bar = document.getElementById('p2-bar');
  p1Bar.style.width = p1_pct + '%';
  p2Bar.style.width = p2_pct + '%';
  p1Bar.style.background = p1_pct > 50 ? '#4caf50' : p1_pct > 20 ? '#f9a825' : '#e3350d';
  p2Bar.style.background = p2_pct > 50 ? '#4caf50' : p2_pct > 20 ? '#f9a825' : '#e3350d';

  // Update log
  const log = document.getElementById('log');
  state.log.forEach(line => {
    const p    = document.createElement('p');
    p.textContent = line;
    if (line.includes('super effective')) p.className = 'highlight';
    if (line.includes('fainted') || line.includes('wins')) p.className = 'green';
    if (line.includes('not very')) p.className = 'red';
    log.appendChild(p);
  });
  log.scrollTop = log.scrollHeight;

  // Shake on hit
  if (state.log.some(l => l.includes('damage'))) {
    const el = document.getElementById('p2-sprite');
    el.classList.remove('shake');
    void el.offsetWidth;
    el.classList.add('shake');
  }

  if (state.over) {
    const winner  = state.winner === 'p1' ? p1.name : p2.name;
    document.getElementById('result-text').textContent = `🏆 ${winner} wins!`;
    document.getElementById('result').classList.add('visible');
    document.querySelectorAll('.move-btn').forEach(b => b.disabled = true);
  }
}

function renderMoves() {
  const grid = document.getElementById('moves');
  grid.innerHTML = '';
  state.p1_moves.forEach((move, i) => {
    const btn   = document.createElement('button');
    btn.className = 'move-btn';
    const color = TYPE_COLORS[move.type] || '#666';
    const pwr   = move.power > 0 ? `PWR ${move.power}` : 'Status';
    btn.innerHTML = `
      <div class="move-name">${move.name}</div>
      <div class="move-meta" style="color:${color}">${move.type} · ${pwr} · ACC ${move.accuracy}%</div>`;
    btn.onclick = () => useMove(i);
    grid.appendChild(btn);
  });
}

async function useMove(idx) {
  if (state?.over) return;
  document.querySelectorAll('.move-btn').forEach(b => b.disabled = true);
  const res = await fetch('/api/battle/move', {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({move_idx: idx})
  });
  state = await res.json();
  updateUI();
  if (!state.over) {
    document.querySelectorAll('.move-btn').forEach(b => b.disabled = false);
  }
}

function rematch() {
  state = null;
  document.getElementById('arena').classList.remove('visible');
  document.getElementById('setup').style.display = 'block';
  document.getElementById('log').innerHTML = '';
  document.getElementById('result').classList.remove('visible');
}
</script>
</body></html>"""

if __name__ == "__main__":
    print("\n  🌐 Pokedex + Battle running!")
    print("  Open http://localhost:5000 in your browser\n")
    app.run(debug=True)
