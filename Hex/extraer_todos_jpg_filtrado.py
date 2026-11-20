from pathlib import Path


def extraer_todos_los_jpg(
    ruta_entrada: str,
    carpeta_salida: str = "extraidos",
    min_bytes: int = 10_240,
) -> None:
  """Extrae bloques desde cada FF D8 hasta el primer FF D9 posterior,

  ignorando bloques mas pequenos que `min_bytes` y guardando los validos
  en bruto sin modificar ningun byte.
  """
  SOI = b"\xff\xd8"
  EOI = b"\xff\xd9"

  datos = Path(ruta_entrada).read_bytes()
  salida_dir = Path(carpeta_salida)
  salida_dir.mkdir(parents=True, exist_ok=True)

  cursor = 0
  guardados = 0
  ignorados = 0

  while True:
    inicio = datos.find(SOI, cursor)
    if inicio == -1:
      break

    fin_eoi = datos.find(EOI, inicio + 2)
    if fin_eoi == -1:
      print(
          f"Aviso: se encontro FF D8 en byte {inicio} (0x{inicio:X}) sin cierre"
          " FF D9 posterior. Se detiene la busqueda."
      )
      break

    fin_bloque = fin_eoi + 2
    tamano = fin_bloque - inicio

    if tamano < min_bytes:
      ignorados += 1
      print(
          f"[IGNORADO] {tamano} bytes (< {min_bytes}) en rango"
          f" 0x{inicio:X}..0x{fin_bloque:X}"
      )
    else:
      bloque_jpg = datos[inicio:fin_bloque]
      guardados += 1
      nombre_archivo = salida_dir / f"imagen_{guardados:02d}.jpg"
      nombre_archivo.write_bytes(bloque_jpg)

      print(
          f"[{guardados:02d}] {nombre_archivo} | {tamano} bytes | rango"
          f" 0x{inicio:X}..0x{fin_bloque:X}"
      )

    # Avanzamos siempre al final del bloque actual para seguir buscando
    cursor = fin_bloque

  print(
      f"\nListo: {guardados} guardada(s), {ignorados} ignorada(s) (umbral:"
      f" {min_bytes} bytes) en '{salida_dir}'."
  )


if __name__ == "__main__":
  archivo_origen = "archivo_contenedor.bin"  # Cambia por tu archivo
  # Ejemplo: 10240 bytes = 10 KB; pon 0 para no ignorar nada
  extraer_todos_los_jpg(
      archivo_origen, carpeta_salida="jpg_extraidos", min_bytes=10_240
  )
