# WhatsApp CHARLIE CROSS BOT 🤖

Un bot automatizado para enviar mensajes masivos de WhatsApp usando Selenium y Django.

## Caracteristicas

- **Envio masivo de mensajes** - Envia mensajes personalizados a multiples contactos
- **Soporte de archivos adjuntos** - Envia imagenes, PDFs, documentos y mas
- **Carga desde Excel** - Importa contactos y mensajes desde archivos `.xlsx`
- **Interfaz web moderna** - Panel de control intuitivo y en espanol
- **Seguimiento en tiempo real** - Monitorea el progreso de envio en vivo
- **Manejo de errores** - Reintentos automaticos y registro de fallos

## Requisitos

- Python 3.10 o superior
- Google Chrome instalado
- Cuenta de WhatsApp activa

## Instalacion

1. **Clona el repositorio**
   ```bash
   git clone https://github.com/TU_USUARIO/whatsapp-charlie-cross-bot.git
   cd whatsapp-charlie-cross-bot
   ```

2. **Crea un entorno virtual**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Instala las dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecuta las migraciones**
   ```bash
   python manage.py migrate
   ```

5. **Inicia el servidor**
   ```bash
   python manage.py runserver
   ```

6. **Abre el navegador**
   ```
   http://localhost:8000
   ```

## Uso

### Formato del archivo Excel

| Columna A | Columna B | Columna C |
|-----------|-----------|-----------|
| **Numero de Telefono** | **Texto del Mensaje** | **Nombre del Archivo** (opcional) |
| 5512345678 | Hola! Tu pedido esta listo. | factura.pdf |
| 5587654321 | Hola! Aqui esta tu recibo. | recibo.jpg |

> Los numeros sin codigo de pais usaran automaticamente +52 (Mexico)

### Pasos para enviar mensajes

1. **Sube tu archivo Excel** con los contactos y mensajes
2. **Adjunta archivos** (opcional) si tu Excel hace referencia a ellos
3. **Previsualiza** los mensajes antes de enviar
4. **Inicia el envio** - Se abrira Chrome con WhatsApp Web
5. **Escanea el codigo QR** de WhatsApp (solo la primera vez)
6. **Monitorea el progreso** en tiempo real

## Notas Importantes

- **Primera vez**: Deberas escanear el codigo QR de WhatsApp Web
- **Sesion persistente**: La sesion se guarda en `chrome_profile/` para no volver a escanear
- **Limites de WhatsApp**: Usa con responsabilidad para evitar restricciones de cuenta
- **Intervalos**: El bot incluye delays aleatorios entre mensajes para simular uso humano

## Seguridad

**NUNCA subas a GitHub:**
- `chrome_profile/` - Contiene tu sesion de WhatsApp
- `db.sqlite3` - Contiene numeros de telefono y mensajes
- Archivos `.env` con credenciales

## Estructura del Proyecto

```
whatsapp_sender/
├── messenger/
│   ├── templates/          # Plantillas HTML
│   ├── views.py           # Vistas de Django
│   ├── models.py          # Modelos de base de datos
│   ├── forms.py           # Formularios
│   └── whatsapp_bot.py    # Bot de Selenium
├── static/
│   └── css/style.css      # Estilos
├── media/uploads/         # Archivos subidos
├── chrome_profile/        # Sesion de Chrome
└── manage.py
```

## Contribuciones

Las contribuciones son bienvenidas! Por favor:

1. Haz fork del proyecto
2. Crea tu rama de feature (`git checkout -b feature/NuevaFuncion`)
3. Commit tus cambios (`git commit -m 'Agregar nueva funcion'`)
4. Push a la rama (`git push origin feature/NuevaFuncion`)
5. Abre un Pull Request

## Licencia

Este proyecto esta bajo la Licencia MIT.

## Desarrollado con

- [Django](https://www.djangoproject.com/) - Framework web
- [Selenium](https://selenium.dev/) - Automatizacion del navegador
- [openpyxl](https://openpyxl.readthedocs.io/) - Lectura de archivos Excel

---


