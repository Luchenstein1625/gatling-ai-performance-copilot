# Presentacion Capstone - Guia para levantar la app

Esta carpeta contiene la presentacion web del proyecto Capstone.

## Requisitos

- Node.js 22.13 o superior
- npm 10 o superior

Puedes validar versiones con:

```bash
node -v
npm -v
```

## Levantar la app en local

1. Entra a la carpeta Presentacion:

```bash
cd Presentacion
```

2. Instala dependencias:

```bash
npm install
```

3. Inicia el servidor de desarrollo:

```bash
npm run dev
```

4. Abre en tu navegador:

```text
http://127.0.0.1:5173
```

Si ese puerto esta ocupado, Vite mostrara otro en consola.

## Atajos por sistema operativo

### Windows

Tambien puedes usar:

```powershell
iniciar-windows.bat
```

### macOS y Linux

Tambien puedes usar:

```bash
chmod +x iniciar.sh
./iniciar.sh
```

## Problemas comunes

### Error: Missing script "dev"

Esto ocurre cuando ejecutas el comando en una carpeta incorrecta.

Solucion:

```bash
cd Presentacion
npm run dev
```

### Error: Could not resolve ./.openai/hosting.json

Si falta ese archivo, crea la carpeta y el archivo:

```bash
mkdir -p .openai
cat > .openai/hosting.json << 'EOF'
{
	"d1": "",
	"r2": ""
}
EOF
```

Luego vuelve a ejecutar:

```bash
npm run dev
```

## Comandos utiles

- Ejecutar pruebas:

```bash
npm test
```

- Exportar PDF (con la app corriendo en otra terminal):

```bash
npm run export:pdf
```

