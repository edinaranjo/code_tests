"""
=============================================================
Laboratorio: Generación masiva de configuraciones Cisco
Autor: Curso de DevOps

Descripción:
Este script genera automáticamente archivos de configuración
para routers Cisco utilizando una plantilla Jinja2 y la
información almacenada en un archivo CSV.

Flujo de trabajo:

1. Leer el archivo CSV.
2. Procesar cada fila del archivo.
3. Construir las variables que utilizará Jinja2.
4. Renderizar la plantilla.
5. Generar un archivo de configuración por cada equipo.
6. Registrar el resultado mediante logging.

=============================================================
"""

# ============================================================
# Importación de librerías
# ============================================================

import csv
import logging
from pathlib import Path
from ipaddress import IPv4Network

from jinja2 import Environment, FileSystemLoader


# ============================================================
# Configuración del sistema de logging
# ============================================================
#
# logging permitirá mostrar mensajes informativos durante la
# ejecución del programa.
#
# INFO      -> Operaciones realizadas correctamente.
# ERROR     -> Errores en una fila determinada.
# CRITICAL  -> Errores que impiden continuar.
#
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)


# ============================================================
# Función: crear_valores_jinja()
# ============================================================
#
# Objetivo:
#
# Construir un diccionario con todas las variables que serán
# utilizadas posteriormente por la plantilla Jinja2.
#
# Entrada:
#
# linea -> corresponde a una fila del archivo CSV.
#
# Salida:
#
# diccionario con las variables de Jinja2.
#
# ============================================================

def crear_valores_jinja(linea):

    try:

        # Crear un objeto IPv4Network a partir de la subred.
        # strict=False permite que, si el CSV contiene una dirección IP
        # perteneciente a la red (por ejemplo 10.230.0.25/24), Python
        # calcule automáticamente la dirección de red (10.230.0.0/24)
        # en lugar de generar una excepción.
        
        subnet = IPv4Network(
            linea["SUBRED/24"] + "/24",
            strict=False
        )

        # ----------------------------------------------------
        # Construir las variables que utilizará la plantilla
        # ----------------------------------------------------

        valores = {

            # Nombre del router
            "HOSTNAME":
                f"{linea['PAIS']}"
                f"{linea['ESTADO']}"
                f"RTR{linea['ID_SITIO']}",

            # Dirección IP de administración
            "IP_MGMT":
                subnet.network_address + 254,

            # Dirección IP de datos
            "IP_DATOS":
                subnet.network_address + 1,

            # Lista de servidores DHCP Helper
            "DATA_HELPER": [
                "172.18.25.1",
                "172.18.26.2",
                "172.18.27.3"
            ],

            # Información del sitio
            "SUBRED_SITIO":
                linea["SUBRED/24"],

            "REGION":
                linea["REGION"],

            # Servidores Syslog
            "IP_SYSLOG_N":
                "192.168.10.254",

            "IP_SYSLOG_S":
                "192.168.33.1"

        }

        # Retornar todas las variables
        return valores

    except Exception as e:

        raise ValueError(
            f"Error procesando la subred "
            f"{linea.get('SUBRED/24')}: {e}"
        )


# ============================================================
# Función: crear_config_jinja()
# ============================================================
#
# Objetivo:
#
# Generar el archivo de configuración Cisco a partir de la
# plantilla Jinja2.
#
# ============================================================

def crear_config_jinja(
        template_env,
        plantilla,
        valores):

    try:

        # ----------------------------------------------------
        # Cargar la plantilla Jinja2
        # ----------------------------------------------------

        template = template_env.get_template(plantilla)

        # ----------------------------------------------------
        # Renderizar la plantilla utilizando las variables
        # generadas anteriormente.
        # ----------------------------------------------------

        configuracion = template.render(valores)

        # ----------------------------------------------------
        # Si el directorio configs no existe, se crea
        # automáticamente.
        # ----------------------------------------------------

        Path("./configs").mkdir(exist_ok=True)

        # ----------------------------------------------------
        # Construir el nombre del archivo de salida.
        # ----------------------------------------------------

        archivo = Path("./configs") / \
            f"{valores['HOSTNAME']}.txt"

        # ----------------------------------------------------
        # Escribir la configuración en disco.
        # ----------------------------------------------------

        with open(
                archivo,
                "w",
                encoding="utf-8") as salida:

            salida.write(configuracion)

        # ----------------------------------------------------
        # Mostrar mensaje de éxito.
        # ----------------------------------------------------

        logging.info(
            f"Archivo generado correctamente: {archivo}"
        )

    except Exception as e:

        raise RuntimeError(
            f"Error generando la configuración para "
            f"{valores.get('HOSTNAME')}: {e}"
        )


# ============================================================
# Función principal
# ============================================================

def main():

    # --------------------------------------------------------
    # Crear el entorno de Jinja2 indicando dónde se encuentra
    # la plantilla.
    # --------------------------------------------------------

    template_env = Environment(

        loader=FileSystemLoader("./docs")

    )

    try:

        # ----------------------------------------------------
        # Abrir el archivo CSV que contiene la información de
        # todos los sitios.
        # ----------------------------------------------------

        with open(
                "./docs/info_sucursales.csv",
                newline="",
                encoding="utf-8") as csvfile:

            reader = csv.DictReader(csvfile)

            # ------------------------------------------------
            # Procesar una fila del CSV a la vez.
            # ------------------------------------------------

            for linea in reader:

                try:

                    # Crear variables para Jinja2
                    valores = crear_valores_jinja(linea)

                    # Generar configuración Cisco
                    crear_config_jinja(

                        template_env,

                        "plantilla_config.j2",

                        valores

                    )

                except Exception as e:

                    # Si existe un problema únicamente con una
                    # sucursal, se registra el error y el
                    # programa continúa con la siguiente.

                    logging.error(

                        f"Problema con la línea\n"
                        f"{linea}\n"
                        f"{e}"

                    )

    # --------------------------------------------------------
    # El usuario presionó Ctrl+C
    # --------------------------------------------------------

    except KeyboardInterrupt:

        logging.warning(
            "Programa suspendido por el usuario."
        )

    # --------------------------------------------------------
    # El archivo CSV no existe.
    # --------------------------------------------------------

    except FileNotFoundError:

        logging.critical(
            "No se encontró el archivo "
            "'info_sucursales.csv'."
        )

    # --------------------------------------------------------
    # Cualquier otro error inesperado.
    # --------------------------------------------------------

    except Exception as e:

        logging.critical(
            f"Error general: {e}"
        )

    # --------------------------------------------------------
    # Siempre se ejecuta, independientemente del resultado.
    # --------------------------------------------------------

    finally:

        logging.info(
            "Proceso finalizado."
        )


# ============================================================
# Punto de entrada del programa
# ============================================================

if __name__ == "__main__":

    main()
