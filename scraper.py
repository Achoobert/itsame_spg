import os
import re
import json
import requests
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader

# Configuration
GM_PROFILE_URL = "https://startplaying.games/gm/achoobert"  # Replace with your profile
SITE_OUTPUT_DIR = "./site"
ANALYTICS_TAG = """
<!-- Google Analytics Tag -->
<script async src="https://www.googletagmanager.com/gtag/js?id=YOUR-ANALYTICS-ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'YOUR-ANALYTICS-ID');
</script>
"""

# Create output directory structure
os.makedirs(SITE_OUTPUT_DIR, exist_ok=True)
os.makedirs(f"{SITE_OUTPUT_DIR}/games", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# Create template files if they don't exist
if not os.path.exists("templates/base.html"):
    with open("templates/base.html", "w") as f:
        f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}GM Profile{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    {{ analytics_tag|safe }}
</head>
<body class="bg-gray-100">
    <header class="bg-blue-800 text-white p-4">
        <div class="container mx-auto">
            <h1 class="text-2xl font-bold"><a href="/">{{ gm_name }}'s Games</a></h1>
        </div>
    </header>
    
    <main class="container mx-auto p-4">
        {% block content %}{% endblock %}
    </main>
    
    <footer class="bg-gray-800 text-white p-4 mt-8">
        <div class="container mx-auto text-center">
            <p>© {{ current_year }} {{ gm_name }}. Game listings from <a href="{{ gm_profile_url }}" class="underline">StartPlaying.games</a></p>
        </div>
    </footer>
</body>
</html>""")

if not os.path.exists("templates/index.html"):
    with open("templates/index.html", "w") as f:
        f.write("""{% extends "base.html" %}

{% block title %}{{ gm_name }}'s Games{% endblock %}

{% block content %}
    <div class="mb-8">
        <img src="{{ gm_avatar }}" alt="{{ gm_name }}" class="w-32 h-32 rounded-full mx-auto mb-4">
        <h2 class="text-3xl font-bold text-center mb-2">{{ gm_name }}</h2>
        <div class="prose max-w-3xl mx-auto">
            {{ gm_bio|safe }}
        </div>
    </div>

    <h3 class="text-2xl font-bold mb-4">Available Games</h3>
    
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {% for game in games %}
        <div class="bg-white rounded-lg shadow-md overflow-hidden">
            <div class="h-48 bg-cover bg-center" style="background-image: url('{{ game.image }}')"></div>
            <div class="p-4">
                <h4 class="text-xl font-bold mb-2">{{ game.title }}</h4>
                <p class="text-gray-600 mb-4">{{ game.system }}</p>
                <a href="games/{{ game.slug }}.html" class="block bg-blue-600 text-white text-center py-2 px-4 rounded hover:bg-blue-700">View Details</a>
            </div>
        </div>
        {% endfor %}
    </div>
{% endblock %}""")

if not os.path.exists("templates/game.html"):
    with open("templates/game.html", "w") as f:
        f.write("""{% extends "base.html" %}

{% block title %}{{ game.title }} - {{ gm_name }}{% endblock %}

{% block content %}
    <div class="mb-6">
        <a href="/" class="text-blue-600 hover:underline">&larr; Back to All Games</a>
    </div>
    
    <div class="bg-white rounded-lg shadow-lg overflow-hidden">
        <div class="h-64 bg-cover bg-center" style="background-image: url('{{ game.image }}')"></div>
        <div class="p-6">
            <h2 class="text-3xl font-bold mb-2">{{ game.title }}</h2>
            <p class="text-xl text-gray-600 mb-4">{{ game.system }}</p>
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div class="bg-gray-100 p-4 rounded">
                    <h3 class="font-bold text-lg mb-2">Price</h3>
                    <p>{{ game.price }}</p>
                </div>
                <div class="bg-gray-100 p-4 rounded">
                    <h3 class="font-bold text-lg mb-2">Duration</h3>
                    <p>{{ game.duration }}</p>
                </div>
                <div class="bg-gray-100 p-4 rounded">
                    <h3 class="font-bold text-lg mb-2">Players</h3>
                    <p>{{ game.players }}</p>
                </div>
            </div>
            
            <h3 class="text-2xl font-bold mb-4">Description</h3>
            <div class="prose max-w-none mb-8">
                {{ game.description|safe }}
            </div>
            
            <a href="{{ game.original_url }}" target="_blank" class="block bg-blue-600 text-white text-center py-3 px-6 rounded-lg hover:bg-blue-700 text-lg">
                Book This Game
            </a>
        </div>
    </div>
{% endblock %}""")

# Initialize Jinja2 environment
env = Environment(loader=FileSystemLoader("templates"))
from datetime import datetime

# Fetch and parse the GM profile page
response = requests.get(GM_PROFILE_URL)
soup = BeautifulSoup(response.text, "html.parser")

# Extract GM info
gm_info = {}
try:
    # Try to extract GM name and bio
    gm_name_element = soup.select_one("h1.text-2xl")
    gm_info["name"] = gm_name_element.text.strip() if gm_name_element else "Game Master"
    
    # Try to extract GM avatar
    gm_avatar_element = soup.select_one("img.rounded-full")
    gm_info["avatar"] = gm_avatar_element.get("src") if gm_avatar_element else ""
    
    # Try to extract GM bio
    gm_bio_element = soup.select_one("div.whitespace-pre-line")
    gm_info["bio"] = gm_bio_element.text.strip() if gm_bio_element else ""
except Exception as e:
    print(f"Error extracting GM info: {e}")
    gm_info = {"name": "Game Master", "avatar": "", "bio": ""}

# Extract games
games = []
try:
    # Look for game listings - adjust selectors as needed
    game_elements = soup.select("div.border-gray-200.rounded-lg") 
    
    for game_element in game_elements:
        try:
            # Extract game details - these selectors may need adjusting
            title_element = game_element.select_one("h3") or game_element.select_one("h2")
            title = title_element.text.strip() if title_element else "Game Title"
            
            # Game image
            image_element = game_element.select_one("img")
            image = image_element.get("src") if image_element else ""
            
            # Game system
            system_element = game_element.select_one("p.text-gray-500")
            system = system_element.text.strip() if system_element else "RPG System"
            
            # Price, duration, players info - these might need adjustment
            price = "Contact for price"
            duration = "3-4 hours"
            players = "3-6 players"
            
            # Description
            description_element = game_element.select_one("div.mt-2") or game_element.select_one("p.mt-1")
            description = description_element.text.strip() if description_element else "Game description unavailable."
            
            # Game URL
            game_url_element = game_element.select_one("a")
            original_url = ""
            if game_url_element and game_url_element.get("href"):
                href = game_url_element.get("href")
                if not href.startswith("http"):
                    original_url = f"https://startplaying.games{href}"
                else:
                    original_url = href
            else:
                original_url = GM_PROFILE_URL
            
            # Create a slug for the filename
            slug = re.sub(r'[^\w\-]', '', title.lower().replace(' ', '-'))
            
            games.append({
                "title": title,
                "image": image,
                "system": system,
                "price": price,
                "duration": duration,
                "players": players,
                "description": description,
                "original_url": original_url,
                "slug": slug
            })
        except Exception as e:
            print(f"Error processing a game: {e}")

except Exception as e:
    print(f"Error extracting games: {e}")

# If no games were found, add a placeholder
if not games:
    games.append({
        "title": "Sample Game",
        "image": "https://via.placeholder.com/300x200",
        "system": "D&D 5e",
        "price": "$15 per player",
        "duration": "3 hours",
        "players": "3-5 players",
        "description": "This is a placeholder game. Please check back later for actual game listings.",
        "original_url": GM_PROFILE_URL,
        "slug": "sample-game"
    })

# Save data for reference
with open(f"{SITE_OUTPUT_DIR}/data.json", "w") as f:
    json.dump({"gm": gm_info, "games": games}, f)

# Generate index page
template = env.get_template("index.html")
index_html = template.render(
    gm_name=gm_info["name"],
    gm_avatar=gm_info["avatar"],
    gm_bio=gm_info["bio"],
    games=games,
    gm_profile_url=GM_PROFILE_URL,
    current_year=datetime.now().year,
    analytics_tag=ANALYTICS_TAG
)
with open(f"{SITE_OUTPUT_DIR}/index.html", "w") as f:
    f.write(index_html)

# Generate game pages
game_template = env.get_template("game.html")
for game in games:
    game_html = game_template.render(
        gm_name=gm_info["name"],
        game=game,
        gm_profile_url=GM_PROFILE_URL,
        current_year=datetime.now().year,
        analytics_tag=ANALYTICS_TAG
    )
    with open(f"{SITE_OUTPUT_DIR}/games/{game['slug']}.html", "w") as f:
        f.write(game_html)

print(f"Generated static site with {len(games)} games")