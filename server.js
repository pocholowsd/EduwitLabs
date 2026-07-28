const express = require('express');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');
const util = require('util');
const execPromise = util.promisify(exec);

const app = express();
const PORT = 3000;

app.use(express.json());
app.use(express.static('public'));

// Función mágica: Escanea el texto crudo del sistema para encontrar cualquier "COM"
async function encontrarPuertoMagicamente() {
    try {
        const { stdout } = await execPromise('arduino-cli board list');
        // Busca en el texto cualquier cosa que diga "COM" seguido de un número (ej. COM7, COM12)
        const match = stdout.match(/(COM\d+)/i);
        
        if (match) {
            console.log(`[+] Puerto encontrado mágicamente para los niños: ${match[1].toUpperCase()}`);
            return match[1].toUpperCase();
        }
    } catch (error) {
        console.error("[-] Error escaneando puertos:", error);
    }
    return null; 
}

app.post('/upload', async (req, res) => {
    const { code, board } = req.body; 
    const fqbn = board || 'arduino:avr:uno';

    // El servidor hace el trabajo sucio, el niño no tiene que saber nada de esto
    const puertoDetectado = await encontrarPuertoMagicamente();
    
    if (!puertoDetectado) {
        return res.status(400).json({ 
            error: "¡Ups! No encuentro tu Arduino. Asegúrate de que el cable USB esté bien conectado." 
        });
    }

    const sketchDir = path.join(__dirname, 'sketch');
    const sketchFile = path.join(sketchDir, 'sketch.ino');

    if (!fs.existsSync(sketchDir)) {
        fs.mkdirSync(sketchDir);
    }
    fs.writeFileSync(sketchFile, code);

    try {
        console.log(`[*] Compilando el código de los niños...`);
        await execPromise(`arduino-cli compile --fqbn ${fqbn} "${sketchDir}"`);
        
        console.log(`[*] Subiendo automáticamente al ${puertoDetectado}...`);
        const { stdout: uploadOut } = await execPromise(
            `arduino-cli upload -p ${puertoDetectado} --fqbn ${fqbn} "${sketchDir}"`
        );

        res.json({ output: `¡Subido exitosamente!\n${uploadOut}` });
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: error.message || error.stderr });
    }
});

app.listen(PORT, () => {
    console.log(`Servidor mágico iniciado en http://localhost:${PORT}`);
});