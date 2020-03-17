Passerelle connector to communicate with AES (HEALTH RECORDS)
=============================================================

Installation
------------

 - add to Passerelle installed apps settings:
   INSTALLED_APPS += ('passerelle_imio_aes_health',)

 - enable module:
   PASSERELLE_APP_PASSERELLE_IMIO_AES_HEALTH_ENABLED = True


Usage
-----

 - create and configure new connector
   - Title/description: whatever you want
   - Certificate check: uncheck if the service has no valid certificate


Usage in w.c.s.
---------------

