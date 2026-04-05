# 🚗 Car Care - Backend API

Ez a repository tartalmazza a Car Care projekt Django alapú `backend` szolgáltatását. Ez az API felelős a felhasználók azonosításáért, a járművek, szervizesemények és alkatrészek adatainak kezeléséért, valamint a statikus fájlok kiszolgálásáért az admin felülethez.

A rendszer egy modern, szétválasztott (microservice jellegű) architektúrában fut, ahol a frontendet (React/Vite) és a backendet egy Cloudflare Tunnel fogja össze.

## Használt Technológiák
* **Keretrendszer:** Python 3.x, Django, Django REST Framework (DRF)
* **Adatbázis:** SQLite (jelenleg)
* **Statikus fájlok:** WhiteNoise
* **Konténerizáció:** Docker & Docker Compose
* **CI/CD:** GitHub Actions (Self-hosted runner)
* **Hálózat & Forgalomirányítás:** Cloudflare Zero Trust (Tunnels)

## Architektúra és Útvonalak
Éles környezetben a backend egy közös Docker hálózaton (`car_care_net`) osztozik a frontenddel. A Cloudflare végzi a forgalomirányítást a `shitbox.hu` domainen:

* `/api/*` ➡️ Django Backend (API végpontok)
* `/admin/*` ➡️ Django Backend (Beépített admin panel)
* `/static/*` ➡️ Django Backend (WhiteNoise CSS/JS kiszolgálás)
* `/` (Minden más) ➡️ React Frontend (Nginx)

## Fejlesztői Környezet Beállítása

Ha a saját gépeden szeretnéd futtatni a kódot Docker nélkül:

1. **Klónozd a repót:**
    > git clone [https://github.com/orkevili/car-care-backend.git](car-care-backend)

    > cd car-care-backend
2. **Hozz létre egy virtuális környezetet és aktiváld:**
    > python -m venv venv
    - Windows-on: `venv\Scripts\activate`
    - Linux/Mac-en: `source venv/bin/activate`
3. **Telepítsd a csomagokat:**
    > pip install -r requirements.txt
4. **Környezeti változók**
    - Hozz létre egy `.env` fájlt a gyökérkönyvtárban. Példa:
    
        DEBUG=True

        SECRET_KEY=ide_jön_egy_titkos_kulcs

        ALLOWED_HOSTS=localhost,127.0.0.1

5. **Adatbázis migráció és futtatás:**
    > python manage.py migrate

    > python manage.py createsuperuser  # Admin fiók létrehozása

    > python manage.py runserver

## 🐳 Futtatás Dockerrel

A projekt tartalmazza a szükséges `Dockerfile` és `docker-compose.yml` fájlokat az azonnali induláshoz.

1. Konténer felépítése és elindítása a háttérben:
    > docker compose up -d --build

2. Migrációk futtatása a futó konténeren belül:
    > docker exec -it django_car_care python manage.py migrate

3. Statikus fájlok összegyűjtése
    > docker exec -it django_car_care python manage.py collectstatic --noinput

## Főbb API Végpontok

Minden végpont az `/api/` prefix alatt érhető el. A legtöbb végpont használatához Token alapú (Bearer/Token) hitelesítés szükséges.

### Autentikáció & Profil

- `POST /api/register/` - Új felhasználó regisztrálása
- `POST /api/login/` - Bejelentkezés, Token lekérése
- `GET /api/logout/` - Kijelentkezés
- `GET /api/me/` - Aktuális felhasználó adatainak lekérése
- `DELETE /api/account/delete/` - Fiók törlése

### Járművek

- `GET /api/vehicles/` - A felhasználó járműveinek listázása
- `POST /api/vehicles/` - Új jármű hozzáadása
- `PATCH /api/vehicles/<id>/` - Jármű adatainak frissítése
- `DELETE /api/vehicles/<id>/` - Jármű törlése

### Szerviz & Alkatrészek

- `GET /api/vehicles/<id>/services/` - Egy adott jármű szerviztörténete
- `POST /api/vehicles/<id>/services/` - Új szervizesemény rögzítése
- `GET /api/vehicles/<id>/supplies/` - Egy adott járműhöz vett alkatrészek
- `POST /api/vehicles/<id>/supplies/` - Új alkatrész hozzáadása

### Adatkezelés (Export/Import)

- `GET /api/data/export/` - Felhasználói adatok exportálása JSON fájlba.
- `POST /api/data/import/` - Adatok importálása mentésből (JSON)

## 🔄 CI/CD és Deployment

A projekt GitHub Actions segítségével, teljesen automatizálva frissül a szerveren (`self-hosted runner`).
Amikor a `main` ágra push történik, a runner újraépíti a Docker image-et, összegyűjti a statikus fájlokat, és újraindítja a `django_car_care` konténert.