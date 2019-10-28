# Prueba 

Se realizo el api REST utilizando los paquetes indicados aunque se realizaron cambios segun los requerimientos
de lo que se estaba desarrollando

* **requirements.txt** - Se agregaron los paquetes siguiente:

**bcrypt** : Utilizado para hacer el hashing del password
**httpie** : Libreria para hacer request desde la linea de comando. Con sintaxis amigable

Se cambio la estructura del proyecto a lo siguiente:

* database: Paquete en el cual se tiene la configuracion de la instancia de la base de datos  utilizada. En este paquete se planeaba colocar todo los relacionado a la misma, incluyendo configuraciones de diferentes de db dependiendo del entorno (dev, testing, etc)

* models: Paquete donde se definieron todas las clases relacionada a la logica del Api, Errores, Paginación, Usuarios y Notas. Solo Notas y Usuarios se guardan en la db. 

* serializer: Serializer para todas las clase de models (TODO: Para facilidad de uso se esta evaluando colocarlos todos juntos en un solo modulo si es que no se necesitaran crear varios serializer de la misma clase)

* utils: funcione de ayuda para manejar data. Ademas se encuentra la clase QueryComposer la cual es un singleton el cual 
se instancia para manejar todo los relacionado a los urlparameters que se pueden pasar al api (seleccion de columnas de las tablas, paginacion, orden, y filtros de data)

* static: Aqui se encuentra el css para la sección de front-end y el javascript para hacer los request a las apis.

Además se ofrecen los archivos test-data.json para probar la carga de notas en batch. 
el archivo main.html tambien usado para el front-end despues de ingresar en el login


## 1. Funcionalidad básica

  Al correr el script server.py se crea una base de datos nueva con algunos datos precargados. Varias notas y un usuario
  con **email**:test@gmail.com y **password**: test.

  Cada vez que se correr el `server.py`. Se elimina la base de datos y se cargan la data predeterminada nuevamente
  
  Para esta sección se crearon los endpoints siguientes:

  `/api/v1/notes`
  `/api/v1/notes/<id:int>`
  `/api/v1/notes/batchnotes`
  `/api/v1/register`
  `/api/v1/login`
  `/api/v1/users`
  `/api/v1/profile`

  El endpoint de batchnotes se utiliza para cargar varias notas a la vez


  Para probar esta sección se uso la libreria de httpie agregada al requirements.txt

  Algunas consultas utilizadas se presentan a continuaciónÑ

  `http GET :8000/api/v1/notes active==False sort==-created_at pagesize==3`
  `http GET :8000/api/v1/notes sort==-created_at pagesize==3 continuetoken==2`
  `http GET :8000/api/v1/notes fields==active,content,title  sort==+created_at pagesize==3 continuetoken==2`

  Probar la carga multiple de notas

  `http POST :8000/api/v1/notes/batchnotes Content-Type:application/json < test-data.json `

  Los campos que tienen la forma de `name==value` son parámetros de URL

  Un ejemplo con el query mas largo seria:

  `http://localhost:8000/api/v1/notes?fields=active,content,title&sort=+created_at&pagesize=3&continuetoken=2`

  sort: Indica que columna utilizar para mostrar el query
  fields : Indica que campos mostrar del recurso solicitado
  pagesize: cantidad de elementos a mostrar (por defecto 5 excepto en el front-end donde se muestran todos)
  continuetoken: indica cual es la siguiente pagina para seguir viendo el resto de recursos de ser necesario.

  El api soporta paginación, y además en la llamadas a nota devuelve una sección de links para saber cual es el siguiente query que se debe hacer y continuar viendo los otros records.


## 2. Funcionalidades adicionales

  **Serialización y validación**

  Se uso la librería de `marshmallow` indicada en las explicaciones para serializar los datos recibidos en el post,
  asi como tambien para convertir los datos de la db a formato JSON y eviar al cliente. 

  Los campos de los parámetros del URL. Si bien el QueryComposer manejar los errores al aplicar dichos paramteros
  estos errores no se han serializado todavia. LA mayoria de errores serializados son al registrar usarios, loguearlos
  y codificar o decodificar el JWT.

  **Usuario y Autentificación**

  El api tiene métodos para autenticar a los usuarios que se registren. Para verificar el password del usuario que desea conectarse se utiliza la libreria bcrypt. El password recibido se compara con el hash guardado en la db y si coinciden, se le genera un token al usuario.  

  Se creó un decorador llamado `auth_required` el cual verifica si el usuario que esta intentando ingresar a un endpoint
  esta autenticado, de no estarlo, se envia un mensaje de error. Este solo ha sido usado en el endpoint `/api/v1/profile`

  
  **Cliente del API**

  Se creo un cliente web sencillo, donde se presenta una pantalla para login del usuario. Dicho cliente llama a la 
  api y guarda en localStorage y el token JWT generado por el api. Al ingresar correctamente se presenta una pantalla
  en donde se puede seleccionar el botón "Get your Notes" y "Write a note". El primero me devuelve todas las notas creadas
  y el segundo me crea una nota en el sistema. Se deja en la sección de escribir una nota por defecto con el formato correcto para enviar la nota.


# Pendientes:

  * Tomar los datos de errores obtenidos del QueryComposer y serializarlos con la clase de ErrorObject
  * Generar la documentación del Api con Swagger.
  * Agregar los test de los endpoints y todas las clases
  * Agregar a los filtros la opcion de filtrar por rangos (< some-date). (Usar operator en python y agregar el simbolo gt:date).
  * Agregar el decorador `auth_required` en los otros endpoints para bloquear toda el api.
  * Terminar de integrar el front end con toda la funcionalidad del API. Mejorar la interfaz de usuario.
  * Utilizar el campo de fecha de expiracion en la db para invalidar el token.
  * Se debe generar logica para desloguear al usuario del sistema.


# Notas

* Fue necesario actualizar la libreria de `marshmallow y peewee` en el requirements debido a que la version que se encontraba en 
el repositorio original no tenias algunos de los metodos utilizados en este proyecto.

# Enunciado

Enunciado origina lde la prueba

# Creación de un API REST

La prueba consistirá en crear un simple API REST para un único recurso, la prueba se dividirá en una funcionalidad básica y en funcionalidades adicionales que sumarán puntos a la evaluación. 

Este repositorio contiene los archivos base, los cambios realizados deben subirse en un repositorio propio, el link de ese repositorio debe enviarse por email.

## 1. Funcionalidad básica
Se desea un endpoint para poder administrar **notas** (crear y listar), los datos se guardará en una base de datos **sqlite**. Para ello se utilizarán los siguientes paquetes de Python.
* [peewee](http://docs.peewee-orm.com/en/latest/ "peewee") (ORM)
* [bottle](https://bottlepy.org/docs/dev/ "bottle") (miniframework web)

Los campos que tendrá el modelo no son relevantes.

## 2. Funcionalidades adicionales
Las siguientes funcionalidades se construirán sobre la funcionalidad base.

**Serialización y validación**

Se desea validar los datos que se reciben via POST y mostrar los errores al usuario que usa el API, serializar la lista de objetos para enviarlas como json. Para ello se utilizará la librería [marshmallow](https://marshmallow.readthedocs.io/en/latest/ "marshmallow").

**Usuario y Autentificación**

Se desea que el API sea restringido mediante algún método de autenficación.

**JWT**

Se desea que el usuario se autentifique mediante json web tokens, para ello se utializará la librería [pyjwt](https://github.com/jpadilla/pyjwt "pyjwt")

**Autorización**

Se desea asociar una **nota** con un **usuario**, de tal manera que cada usuario solo pueda ver sus propias notas.

**Cliente del API**

Se desea tener un cliente web que haga uso del API desde frontend (html y javascript). Ver siguiente sección.

# Estructura de archivos
El repositorio contiene archivos que sirven como guia, pero se deja la libertad de hacer los cambios que se consideren necesarios.
* **.gitignore** - Archivos ignorados por git, añadir la base de datos sqlite que se genere.
* **requirements.txt** - Los paquetes python que se utilizarán para la prueba. Se recomienda usar un entorno virtual (ejem. [virtualenv](https://virtualenv.pypa.io/en/stable/ "virtualenv")) para instalarlos.
* **server.py** - Contendrá tóda la lógica del api, este correrá en el puerto 8000.
* **client.py** - Un pequeño servidor que corre en el puerto 5000 y sirve el archivo index.html, aquí no se necesita hacer ninguna modificación.
* **index.html** - Donde idealmente deberá estar toda la lógica para loguearse y mostrar los datos del api.

# Objetivos de la prueba
* Evaluar el conocimiento general del lenguaje Python.
* Evaluar el conocimiento en arquitecturas web (MVC, REST).
* Comprobar el conocimiento independientemente de la herramienta / framework.
* Evaluar buenas prácticas en el código relacionadas con Python (pep8).
* Evaluar conocimientos basicos de frontend.
* Evaluar el modelo mental que se tiene para la organización de classes, funciones, módulos.








