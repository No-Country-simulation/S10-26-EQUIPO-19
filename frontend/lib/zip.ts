// Arma un ZIP en el navegador sin dependencias externas (9.6): método "store" (sin compresión),
// suficiente para los archivos de texto de una propuesta y compatible con cualquier descompresor.

export type ZipFile = {
  /** Nombre del archivo dentro del ZIP, sin carpetas. */
  name: string;
  /** Contenido de texto; se codifica como UTF-8. */
  content: string;
};

const encoder = new TextEncoder();

const CRC_TABLE = (() => {
  const table = new Uint32Array(256);
  for (let n = 0; n < 256; n++) {
    let value = n;
    for (let bit = 0; bit < 8; bit++) value = value & 1 ? 0xedb88320 ^ (value >>> 1) : value >>> 1;
    table[n] = value >>> 0;
  }
  return table;
})();

function crc32(bytes: Uint8Array): number {
  let crc = 0xffffffff;
  for (let i = 0; i < bytes.length; i++) crc = CRC_TABLE[(crc ^ bytes[i]) & 0xff] ^ (crc >>> 8);
  return (crc ^ 0xffffffff) >>> 0;
}

/** Formato de fecha y hora de MS-DOS que usa el encabezado ZIP. */
function dosDateTime(date: Date) {
  return {
    time: (date.getHours() << 11) | (date.getMinutes() << 5) | Math.floor(date.getSeconds() / 2),
    date: ((Math.max(date.getFullYear(), 1980) - 1980) << 9) | ((date.getMonth() + 1) << 5) | date.getDate(),
  };
}

const LOCAL_HEADER = 30;
const CENTRAL_HEADER = 46;
const END_RECORD = 22;

export function createZip(files: ZipFile[], date = new Date()): Blob {
  const stamp = dosDateTime(date);
  const entries = files.map((file) => {
    const name = encoder.encode(file.name);
    const data = encoder.encode(file.content);
    return { name, data, crc: crc32(data) };
  });
  const localSize = entries.reduce((total, e) => total + LOCAL_HEADER + e.name.length + e.data.length, 0);
  const centralSize = entries.reduce((total, e) => total + CENTRAL_HEADER + e.name.length, 0);

  const output = new Uint8Array(localSize + centralSize + END_RECORD);
  const view = new DataView(output.buffer);
  const u16 = (offset: number, value: number) => view.setUint16(offset, value, true);
  const u32 = (offset: number, value: number) => view.setUint32(offset, value >>> 0, true);

  // Encabezados locales con el contenido: versión 2.0, flag UTF-8, método "store", fecha, CRC y tamaños.
  let position = 0;
  const offsets: number[] = [];
  for (const entry of entries) {
    offsets.push(position);
    u32(position, 0x04034b50);
    u16(position + 4, 20);
    u16(position + 6, 0x0800);
    u16(position + 8, 0);
    u16(position + 10, stamp.time);
    u16(position + 12, stamp.date);
    u32(position + 14, entry.crc);
    u32(position + 18, entry.data.length);
    u32(position + 22, entry.data.length);
    u16(position + 26, entry.name.length);
    u16(position + 28, 0);
    position += LOCAL_HEADER;
    output.set(entry.name, position);
    position += entry.name.length;
    output.set(entry.data, position);
    position += entry.data.length;
  }

  // Directorio central: los mismos datos más la posición de cada encabezado local.
  const centralStart = position;
  entries.forEach((entry, index) => {
    u32(position, 0x02014b50);
    u16(position + 4, 20);
    u16(position + 6, 20);
    u16(position + 8, 0x0800);
    u16(position + 10, 0);
    u16(position + 12, stamp.time);
    u16(position + 14, stamp.date);
    u32(position + 16, entry.crc);
    u32(position + 20, entry.data.length);
    u32(position + 24, entry.data.length);
    u16(position + 28, entry.name.length);
    u16(position + 30, 0);
    u16(position + 32, 0);
    u16(position + 34, 0);
    u16(position + 36, 0);
    u32(position + 38, 0);
    u32(position + 42, offsets[index]);
    position += CENTRAL_HEADER;
    output.set(entry.name, position);
    position += entry.name.length;
  });

  // Fin del directorio central: sin comentario ni ZIP64 (los archivos son pequeños).
  u32(position, 0x06054b50);
  u16(position + 4, 0);
  u16(position + 6, 0);
  u16(position + 8, entries.length);
  u16(position + 10, entries.length);
  u32(position + 12, position - centralStart);
  u32(position + 16, centralStart);
  u16(position + 20, 0);

  return new Blob([output], { type: "application/zip" });
}
