# Calidad_Software
Archivos de pruebas de calidad

Uso:
- Copiar el repositorio
- En una terminal ir al directorio del projecto
- Crear un ambiente virtual: ``python -m venv .venv ``
- Activarlo con ``source .venv/bin/activate``  o usando ``.venv\Scripts\activate`` en Windows
- Instalar los paquetes necesarios: ``pip install -r requirements.txt``
- *Ahora se puede usar la carga automatica* ~Registrar un usuario y modificar el archivocon el usuario o contraseña ej:~
  * EMAIL = "admin@example.com"
  * PASSWORD = "admin"
- Cambiar BASE_URL de http://localhost:3000 a https://juice-shop.herokuapp.com/
- Correr el codigo con:
  *  ``python juice_shop_login_test.py``
  *  ``python juice_shop_register_from_csv.py``
  *  ``locust -f locustfile2.py --host http://localhost:3000 --headless -t 10m --html stress_report.html --csv stress_results``
  *  ``locust -f locustfile.py --host http://localhost:3000 -u 50 -r 5 -t 5m --headless --html load_report.html --csv load_results``
