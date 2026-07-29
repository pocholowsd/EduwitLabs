Compilador Web y Monitor Serial para Arduino
Herramienta web local basada en Node.js y la API Web Serial para compilar, subir código y monitorear placas Arduino directamente desde el navegador.

Requisitos e Instalación
1. Prerrequisitos (Node.js y Arduino CLI)
     Abre tu terminal en Windows y ejecuta los siguientes comandos:
     Instalar Node.js:
       winget install OpenJS.NodeJS
   
     Instalar Arduino CLI:
       winget install Arduino.cli
       (Nota: Si el comando de winget para arduino-cli no funciona, la otra opción es:)
       Método alternativo de instalación manual:
       Abre tu navegador y descarga el archivo ZIP oficial de arduino-cli.
       Descomprímelo en una carpeta fácil (por ejemplo, crea una carpeta llamada C:\arduino-cli).
       Ejecuta:
       [Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\arduino-cli", [EnvironmentVariableTarget]::User)

     Configuración Inicial de Arduino CLI:
     Una vez instalado el CLI, inicializa el archivo de configuración y descarga el núcleo para Arduino AVR:
       arduino-cli config init
       arduino-cli core update-index
       arduino-cli core install arduino:avr
   
Estructura del proyecto:
Organiza los archivos de tu proyecto de la siguiente manera:  
compilador-web-arduino/
├── server.js
└── public/
    ├── index.html
    └── monitor.html
    
Instalar dependencias del servidor y ejecutar
1. Inicializar el proyecto e instalar dependencias
     npm init -y
     npm install express cors
   
2. Iniciar el servidor
     node server.js
