# Videoflix Backend API

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/HTK-MM/Videoflix_backend/blob/master/README.MD) [![de](https://img.shields.io/badge/lang-de-yellow.svg)](https://github.com/HTK-MM/Videoflix_backend/blob/master/README.de.md)

## Beschreibung

Videoflix Backend ist die API einer Video-Streaming-App, entwickelt mit Django und Django REST Framework. Es stellt Schnittstellen für Benutzerkonten, Video-Uploads, Kategorien, Watchlists und mehr bereit.

## Hauptfunktionen

- Benutzerregistrierung, Login und Passwort-Zurücksetzung  
- JWT-Authentifizierung mit HTTP-only Cookies  
- Videos hochladen und automatisch Thumbnails generieren  
- Videos mit Celery und FFmpeg in verschiedene Auflösungen konvertieren  
- HLS-Streams für flüssige Wiedergabe erzeugen  
- Video-Kategorien erstellen und auflisten  
- Videos zu einer persönlichen Watchlist hinzufügen  
- Wiedergabeverlauf für jeden Nutzer verfolgen  
- Läuft mit Docker und PostgreSQL  


## Verwendete Technologien

- **Python 3.x** – Programmiersprache  
- **Django 5.2.3** – Web-Framework  
- **Django REST Framework 3.16.0** – API-Entwicklung  
- **SimpleJWT** – JWT-Authentifizierung mit Cookies  
- **Redis + django-rq** – Hintergrundaufgaben mit Job-Queues  
- **FFmpeg + ffmpeg-python** – Videobearbeitung  
- **PostgreSQL** – Produktionsdatenbank  
- **Gunicorn** – WSGI-Server für den Einsatz  
- **Whitenoise** – Ausliefern von statischen Dateien in Produktion  
- **Docker** – Containerisierung und Umgebungsverwaltung  

## Installation

### Manuelle Installation

1. Klonen Sie das Repository:
   ```bash
   git clone https://github.com/HTK-MM/VideoflixBackend/.git
    cd projekt
   ```

2. Erstellen und aktivieren Sie eine virtuelle Umgebung:
    ````bash    
    python -m venv venv
       source venv/bin/activate  #On Windows: venv\Scripts\activate
    ````

3. Installieren Sie die Abhängigkeiten:
    ````bash 
    pip install -r requirements.txt
    ````

4. Konfigurieren Sie die Datenbank und führen Sie Migrationen durch:
    ````bash 
    python manage.py migrate
    ````

5. Erstellen Sie einen Superuser (optional für den Zugriff auf das Admin-Panel):
    ````bash 
    python manage.py createsuperuser
    ````

6. Starten Sie den Entwicklungsserver:
    ````bash 
    python manage.py runserver
    ````

### Docker Setup

Alternativ kann das Backend auch mit Docker betrieben werden.

1. Stelle sicher, dass Docker und Docker Compose installiert sind.
   
2. Container starten:
    ````bash   
    docker compose up --build
    ````

3. API unter http://localhost:8000 aufrufen
   
4. Einmalig Superuser im Container anlegen:
   ````bash   
    docker-compose exec web python manage.py createsuperuser
    ```` 

5. Datenbank migrieren:
    ````bash 
    docker-compose exec web python manage.py migrate
    ````

6. Container stoppen:
    ````bash   
    docker-compose down
    ````

## Environment Variables

Für die korrekte Konfiguration müssen mehrere Environment-Variablen gesetzt werden.

Eine Beispieldatei  `.env.template` ist im Repository enthalten, mit allen nötigen Schlüsseln und Platzhalterwerten.

Zur Einrichtung kopiere die Datei  `.env.template` in `.env` und passe die Werte an:

    ````bash   
    cp .env.template .env
    # Danach die Datei .env mit den echten Werten bearbeiten (Datenbank, Secrets, Email, etc.)
    ````

## API Basis-Pfad

Alle API-Endpunkte haben den Präfix `/api/`.  
Beispiele:  
- `GET /api/video/` – Gibt eine Liste aller Videos zurück.
- `POST /api/login/` – Authentifiziert einen Nutzer und liefert ein JWT.

Die Django URL-Konfiguration `urlpatterns` umfasst:

    ```python
urlpatterns = [
    path('admin/', admin.site.urls),                  # Admin interface
    path('api/', include('videoflix_app.api.urls')),  # Haupt API
    path('django-rq/', include('django_rq.urls')),    # Überwachung der Task-Queues
]
    ```

## API Endpunkte

Die Videoflix API bietet folgende Endpunkte:

### :small_blue_diamond: Authentifizierung & Nutzer

-   ````**POST /register/**```` - Neuen Nutzer registrieren.
-   ````**GET /activate/<uidb64>/<token>/**```` - Kontoaktivierung per Token (E-Mail).
-   ````**POST /login/**```` -  Anmeldung mit JWT (im Cookie gespeichert).
-   ````**POST /token/refresh/**```` -   JWT Token erneuern.
-   ````**POST /logout/**```` -  Abmelden und Authentifizierungs-Cookies löschen.
-   ````**GET /users/check-login-register/**```` -  Prüfen, ob Anmeldung oder Registrierung nötig ist.
-   ````**POST /password_reset/**```` -  Passwort zurücksetzen anfordern.
-   ````**POST /password_confirm/<uidb64>/<token>/**```` -  Passwort zurücksetzen bestätigen.
-   ````**`GET` | `PUT` | `DELETE` /user/**```` -  Verwaltung des authentifizierten Nutzerprofils.
  
### :small_blue_diamond:  Kategorien
-   ````**GET /categories/**```` - Alle verfügbaren Videokategorien auflisten. 
-   ````**POST /categories/**```` - Neue Kategorie erstellen.   

### :small_blue_diamond: Videos

-   ````**GET /video/**```` - Liste aller Videos abrufen. 
-   ````**GET /video/<id>/**```` - Details zu einem Video abrufen.
-   ````**GET /video/<movie_id>/<resolution>/index.m3u8**```` - HLS Manifest abrufen.
-   ````**GET /video/<movie_id>/<resolution>/<segment>/**```` - HLS Video-Segment abrufen.

### :small_blue_diamond: Watchlist

-   ````**`GET` | `POST` /watchlist/**```` - Auf persönliche Watchlist zugreifen oder Einträge hinzufügen.
-   ````**`GET` | `DELETE` /watchlist-entries/**```` - Einzelne Watchlist-Einträge verwalten.
   
## Tests
   
### Tests lokal ausführen
1. Virtuelle Umgebung aktivieren und Abhängigkeiten installieren:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ````
2. Migrationen anwenden und Tests starten:
    ````bash   
    python manage.py migrate
    python manage.py test
    ````

### Tests mit Docker ausführen
1. Container starten:
    ````bash   
    docker-compose up 
    ````    
2. Migrationen im Container anwenden (falls noch nicht geschehen):
   ````bash   
    docker-compose exec web python manage.py migrate
    ````    
3. Tests im Container ausführen:
    ````bash   
    docker-compose exec web python manage.py test
    ````    
4. Container stoppen:
    ````bash   
    docker-compose down
    ````   

