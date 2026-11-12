// API mínima de reservas: capa de aplicación (subred privada), habla con MySQL en la subred de datos.
const express = require('express');
const mysql = require('mysql2/promise');
const os = require('os');
const dns = require('dns').promises;
const path = require('path');

const app = express();
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

const pool = mysql.createPool({
  host: process.env.DB_HOST, user: process.env.DB_USER, password: process.env.DB_PASS,
  database: process.env.DB_NAME, connectionLimit: 5, connectTimeout: 5000, dateStrings: true,
});

async function prepararBD() {
  for (;;) {
    try {
      await pool.query(`CREATE TABLE IF NOT EXISTS reservas (
        id INT AUTO_INCREMENT PRIMARY KEY, nombre VARCHAR(80) NOT NULL, sala VARCHAR(40) NOT NULL,
        fecha DATE NOT NULL, creada TIMESTAMP DEFAULT CURRENT_TIMESTAMP)`);
      return console.log('Base de datos lista');
    } catch (e) {
      console.log('Esperando la base de datos:', e.code || e.message);
      await new Promise(r => setTimeout(r, 5000));
    }
  }
}

const ipLocal = () => Object.values(os.networkInterfaces()).flat()
  .find(i => i.family === 'IPv4' && !i.internal && i.address.startsWith('10.'))?.address
  || Object.values(os.networkInterfaces()).flat().find(i => i.family === 'IPv4' && !i.internal)?.address;

app.get('/api/health', (req, res) => res.json({ status: 'ok' }));

// Muestra por qué capa pasó la petición: útil para evidenciar la segmentación.
app.get('/api/info', async (req, res) => {
  const ipBD = await dns.lookup(process.env.DB_HOST).then(r => r.address).catch(() => null);
  res.json({
    cliente: (req.headers['x-forwarded-for'] || '').split(',')[0] || null,
    balanceador: req.socket.remoteAddress.replace('::ffff:', ''),
    servidorApp: ipLocal(),
    baseDeDatos: ipBD,
  });
});

app.get('/api/reservas', async (req, res) => {
  const [filas] = await pool.query('SELECT id, nombre, sala, fecha FROM reservas ORDER BY fecha, id');
  res.json(filas);
});

app.post('/api/reservas', async (req, res) => {
  const { nombre, sala, fecha } = req.body || {};
  if (!nombre || !sala || !/^\d{4}-\d{2}-\d{2}$/.test(fecha || '')) return res.status(400).json({ error: 'nombre, sala y fecha (AAAA-MM-DD) son obligatorios' });
  const [r] = await pool.query('INSERT INTO reservas (nombre, sala, fecha) VALUES (?, ?, ?)', [nombre, sala, fecha]);
  res.status(201).json({ id: r.insertId, nombre, sala, fecha });
});

app.delete('/api/reservas/:id', async (req, res) => {
  const [r] = await pool.query('DELETE FROM reservas WHERE id = ?', [req.params.id]);
  res.status(r.affectedRows ? 204 : 404).end();
});

app.use((err, req, res, next) => res.status(503).json({ error: 'Base de datos no disponible', detalle: err.code || err.message }));

app.listen(8080, '0.0.0.0', () => console.log('API escuchando en 8080'));
prepararBD();
