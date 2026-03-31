# Alap image: könnyűsúlyú Python
FROM python:3.12-slim

# Munkakönyvtár beállítása a konténeren belül
WORKDIR /app

# Függőségek másolása és telepítése
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# A teljes kódod bemásolása
COPY . .

# Váltás a projekt mappába
WORKDIR /app/car_care

# Django statikus fájlok begyűjtése (opcionális, de ajánlott Nginx-hez)
RUN python manage.py collectstatic --noinput

# A Gunicorn indítása
# FIGYELEM: A 'Django_car_care.wsgi' részt cseréld le a te projekted nevére, 
# abban a mappában van a wsgi.py fájl!
CMD ["gunicorn", "car_care.wsgi:application", "--bind", "0.0.0.0:8000"]