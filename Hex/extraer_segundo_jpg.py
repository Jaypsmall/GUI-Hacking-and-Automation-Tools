from pathlib import Path


def extraer_jpg_por_indice(ruta_entrada: str, ruta_salida: str, indice: int = 2) -> None:
  """Extrae el N-esimo bloque JPEG (indice=1 es el primero, indice=2 es el segundo)

  desde su marcador FF D8 hasta el primer FF D9 posterior.
  """
  SOI = b"\xff\xd8"  # Start of Image
  EOI = b"\xff\xd9"  # End of Image

  datos = Path(ruta_entrada).read_bytes()

  pos = 0
  encontrados = 0
  inicio_bloque = -1

  # Buscamos el marcador SOI numero `indice`
  while encontrados < indice:
    idx = datos.find(SOI, pos)
    if idx == -1:
      raise ValueError(
          f"No se encontraron {indice} bloques FF D8 (solo se encontraron"
          f" {encontrados})."
      )
    encontrados += 1
    inicio_bloque = idx
    pos = idx + 2

  # Desde ese FF D8, buscamos el primer FF D9 posterior
  fin_soi = datos.find(EOI, inicio_bloque + 2)
  if fin_soi == -1:
    raise ValueError(
        f"Se encontro el inicio FF D8 #{indice} en el byte {inicio_bloque},"
        " pero no hay un FF D9 posterior."
    )

  fin_bloque = fin_soi + 2  # Incluimos los 2 bytes de FF D9
  bloque_jpg = datos[inicio_bloque:fin_bloque]

  Path(ruta_salida).write_bytes(bloque_jpg)
  print(f"Extraido bloque #{indice} correctamente:")
  print(f"  Inicio (FF D8): {inicio_bloque} (0x{inicio_bloque:X})")
  print(f"  Fin (FF D9):    {fin_bloque} (0x{fin_bloque:X})")
  print(f"  Tamano:         {len(bloque_jpg)} bytes")
  print(f"  Guardado en:    {ruta_salida}")


if __name__ == "__main__":
  archivo_origen = "archivo_contenedor.bin"  # Cambia por tu archivo
  archivo_destino = "imagen_2.jpg"
  extraer_jpg_por_indice(archivo_origen, archivo_destino, indice=2)