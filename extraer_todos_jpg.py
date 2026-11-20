from pathlib import Path


def extraer_todos_los_jpg(
    ruta_entrada: str, carpeta_salida: str = "extraidos"
) -> None:
  """Extrae todos los bloques desde cada FF D8 hasta el primer FF D9 posterior,

  guardandolos en bruto sin modificar ningun byte.
  """
  SOI = b"\xff\xd8"
  EOI = b"\xff\xd9"

  datos = Path(ruta_entrada).read_bytes()
  salida_dir = Path(carpeta_salida)
  salida_dir.mkdir(parents=True, exist_ok=True)

  cursor = 0
  contador = 0

  while True:
    inicio = datos.find(SOI, cursor)
    if inicio == -1:
      break  # No hay mas inicios FF D8

    fin_eoi = datos.find(EOI, inicio + 2)
    if fin_eoi == -1:
      print(
          f"Aviso: se encontro FF D8 en byte {inicio} (0x{inicio:X}) sin cierre"
          " FF D9 posterior. Se detiene la busqueda."
      )
      break

    fin_bloque = fin_eoi + 2
    bloque_jpg = datos[inicio:fin_bloque]

    contador += 1
    nombre_archivo = salida_dir / f"imagen_{contador:02d}.jpg"
    nombre_archivo.write_bytes(bloque_jpg)

    print(
        f"[{contador:02d}] {nombre_archivo} | {len(bloque_jpg)} bytes | "
        f"rango 0x{inicio:X}..0x{fin_bloque:X}"
    )

    # Continuamos buscando despues del cierre FF D9 de este bloque
    cursor = fin_bloque

  print(f"\nListo: se extrajeron {contador} bloque(s) en '{salida_dir}'.")


if __name__ == "__main__":
  archivo_origen = "archivo_contenedor.bin"  # Cambia por tu archivo
  extraer_todos_los_jpg(archivo_origen, carpeta_salida="jpg_extraidos")