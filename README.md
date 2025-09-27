# Calidad_Software
Archivos de pruebas de calidad

Uso:
- Copiar el repositorio
- En una terminal ir al directorio del projecto
- Crear un ambiente virtual: 
python -m venv .venv
source .venv/bin/activate      # o usando .venv\Scripts\activate en Windows
pip install selenium webdriver-manager
- Registrar un usuario y modificar el archivocon el usuario o contraseña ej:
EMAIL = "admin@example.com"
PASSWORD = "admin"
- Cambiar BASE_URL de http://localhost:3000 a https://juice-shop.herokuapp.com/
- Correr el codigo con: python juice_shop_login_test.py
