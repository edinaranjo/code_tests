"""Laboratorio de generación masiva de configuraciones Cisco.

Este programa genera automáticamente archivos de configuración
para routers Cisco utilizando una plantilla Jinja2 y la información
almacenada en un archivo CSV.

Flujo de trabajo:
    1. Leer el archivo CSV.
    2. Procesar cada registro.
    3. Construir las variables utilizadas por Jinja2.
    4. Renderizar la plantilla.
    5. Generar un archivo de configuración por dispositivo.
    6. Registrar el resultado mediante logging.
"""

import csv
import logging
import sys
from ipaddress import IPv4Network
from pathlib import Path

from jinja2 import (
    Environment,
    FileSystemLoader,
    StrictUndefined,
    TemplateError,
    select_autoescape,
)

# ============================================================
# Rutas del proyecto
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DOCS_DIR = BASE_DIR / "docs"
CONFIGS_DIR = BASE_DIR / "configs"

CSV_FILE = DOCS_DIR / "info_sucursales.csv"
TEMPLATE_FILE = "plantilla_config.j2"


# ============================================================
# Logging
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)

logger = logging.getLogger(__name__)


# ============================================================
# Función crear_valores_jinja()
# ============================================================


def crear_valores_jinja(linea: dict[str, str]) -> dict[str, object]:
    """Construye las variables utilizadas por la plantilla Jinja2.

    Args:
        linea: Registro obtenido del archivo CSV.

    Returns:
        Diccionario con las variables utilizadas por Jinja2.

    Raises:
        ValueError: Si falta un campo obligatorio o la subred
            especificada no es válida.
    """

    try:
        subnet = IPv4Network(
            f"{linea['SUBRED/24']}/24",
            strict=False,
        )

        valores = {
            "HOSTNAME": (f"{linea['PAIS']}{linea['ESTADO']}RTR{linea['ID_SITIO']}"),
            "IP_MGMT": subnet.network_address + 254,
            "IP_DATOS": subnet.network_address + 1,
            "DATA_HELPER": [
                "172.18.25.1",
                "172.18.26.2",
                "172.18.27.3",
            ],
            "SUBRED_SITIO": linea["SUBRED/24"],
            "REGION": linea["REGION"],
            "IP_SYSLOG_N": "192.168.10.254",
            "IP_SYSLOG_S": "192.168.33.1",
        }

        return valores

    except KeyError as exc:
        raise ValueError(f"Campo obligatorio inexistente: {exc}") from exc

    except ValueError as exc:
        raise ValueError(
            f"Error procesando la subred {linea.get('SUBRED/24')}: {exc}"
        ) from exc


# ============================================================
# Función crear_config_jinja()
# ============================================================


def crear_config_jinja(
    template_env: Environment,
    plantilla: str,
    valores: dict[str, object],
    output_dir: Path = CONFIGS_DIR,
) -> Path:
    """Genera un archivo de configuración Cisco.

    Args:
        template_env: Entorno configurado de Jinja2.
        plantilla: Nombre del archivo de plantilla.
        valores: Variables utilizadas por la plantilla.
        output_dir: Directorio donde se almacenará la configuración.

    Returns:
        Ruta del archivo generado.

    Raises:
        RuntimeError: Si ocurre un error procesando la plantilla
            o escribiendo el archivo.
    """

    try:
        template = template_env.get_template(plantilla)

        configuracion = template.render(**valores)

        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        hostname = str(valores["HOSTNAME"])

        archivo = output_dir / f"{hostname}.txt"

        archivo.write_text(
            configuracion,
            encoding="utf-8",
        )

        logger.info(
            "Archivo generado correctamente: %s",
            archivo,
        )

        return archivo

    except TemplateError as exc:
        raise RuntimeError(
            f"Error procesando la plantilla para {valores.get('HOSTNAME')}: {exc}"
        ) from exc

    except OSError as exc:
        raise RuntimeError(
            f"Error escribiendo la configuración para {valores.get('HOSTNAME')}: {exc}"
        ) from exc


# +--------------------------------------------------------------------------------------
#| Falla Intencional
# +--------------------------------------------------------------------------------------

"""
def ejecutar_comando(comando: str) -> None:
    subprocess.run(
        comando,
        shell=True,
       check=False,
    )

"""


# ============================================================
# Función principal
# ============================================================


def main() -> int:
    """Ejecuta la generación masiva de configuraciones Cisco.

    Returns:
        0 si todas las configuraciones son generadas correctamente.
        1 si ocurre uno o más errores.
        130 si el usuario interrumpe la ejecución.
    """

    template_env = Environment(
        loader=FileSystemLoader(DOCS_DIR),
        undefined=StrictUndefined,
        autoescape=select_autoescape(
            enabled_extensions=("html", "htm", "xml"),
            default_for_string=False,
            default=False,
        ),
    )

    errores = 0
    procesados = 0
    generados = 0

    try:
        with CSV_FILE.open(
            newline="",
            encoding="utf-8",
        ) as csvfile:
            reader = csv.DictReader(csvfile)

            for linea in reader:
                procesados += 1

                try:
                    valores = crear_valores_jinja(linea)

                    crear_config_jinja(
                        template_env,
                        TEMPLATE_FILE,
                        valores,
                        CONFIGS_DIR,
                    )

                    generados += 1

                except (ValueError, RuntimeError) as exc:
                    errores += 1

                    logger.error(
                        "Problema procesando el registro %s: %s",
                        linea,
                        exc,
                    )

        if procesados == 0:
            logger.error("El archivo CSV no contiene registros.")
            return 1

        logger.info(
            "Registros procesados: %d",
            procesados,
        )

        logger.info(
            "Configuraciones generadas: %d",
            generados,
        )

        if errores > 0:
            logger.error(
                "La ejecución terminó con %d error(es).",
                errores,
            )
            return 1

        logger.info("Todas las configuraciones fueron generadas correctamente.")

        return 0

    except KeyboardInterrupt:
        logger.warning("Programa suspendido por el usuario.")

        return 130

    except FileNotFoundError as exc:
        logger.critical(
            "No se encontró un archivo requerido: %s",
            exc.filename,
        )

        return 1

    except OSError as exc:
        logger.critical(
            "Error accediendo a los archivos del proyecto: %s",
            exc,
        )

        return 1

    finally:
        logger.info("Proceso finalizado.")


# ============================================================
# Punto de entrada
# ============================================================

if __name__ == "__main__":
    sys.exit(main())
