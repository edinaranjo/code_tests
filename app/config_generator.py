"""Generador de configuraciones Cisco basado en CSV y Jinja2."""

import csv
import logging
from ipaddress import IPv4Network
from pathlib import Path

from jinja2 import Environment
from jinja2 import FileSystemLoader
from jinja2 import StrictUndefined
from jinja2 import TemplateError

from app.exceptions import SiteDataError
from app.exceptions import TemplateRenderError


logger = logging.getLogger(__name__)


def cargar_sitios(csv_path: Path) -> list[dict[str, str]]:
    """Carga la información de sitios desde un archivo CSV.

    Args:
        csv_path: Ruta del archivo CSV.

    Returns:
        Lista de diccionarios. Cada diccionario representa un sitio.

    Raises:
        FileNotFoundError: Si el archivo CSV no existe.
        ValueError: Si el archivo no contiene registros.
    """

    if not csv_path.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo CSV: {csv_path}"
        )

    with csv_path.open(
        mode="r",
        newline="",
        encoding="utf-8",
    ) as csv_file:
        reader = csv.DictReader(csv_file)
        sitios = list(reader)

    if not sitios:
        raise ValueError(
            "El archivo CSV no contiene registros."
        )

    return sitios


def crear_valores_jinja(
    sitio: dict[str, str],
) -> dict[str, object]:
    """Construye las variables utilizadas por la plantilla Jinja2.

    Args:
        sitio: Registro correspondiente a un sitio.

    Returns:
        Diccionario con variables de configuración.

    Raises:
        SiteDataError: Cuando falta información o la subred es inválida.
    """

    campos_requeridos = {
        "PAIS",
        "ESTADO",
        "ID_SITIO",
        "SUBRED/24",
        "REGION",
    }

    campos_faltantes = campos_requeridos - sitio.keys()

    if campos_faltantes:
        raise SiteDataError(
            "Faltan campos requeridos: "
            f"{', '.join(sorted(campos_faltantes))}"
        )

    try:
        subnet = IPv4Network(
            f"{sitio['SUBRED/24']}/24",
            strict=False,
        )

    except ValueError as exc:
        raise SiteDataError(
            f"Subred inválida: {sitio['SUBRED/24']}"
        ) from exc

    hostname = (
        f"{sitio['PAIS']}"
        f"{sitio['ESTADO']}"
        f"RTR{sitio['ID_SITIO']}"
    )

    return {
        "HOSTNAME": hostname,
        "IP_MGMT": str(subnet.network_address + 254),
        "IP_DATOS": str(subnet.network_address + 1),
        "DATA_HELPER": [
            "172.18.25.1",
            "172.18.26.2",
            "172.18.27.3",
        ],
        "SUBRED_SITIO": sitio["SUBRED/24"],
        "REGION": sitio["REGION"],
        "IP_SYSLOG_N": "192.168.10.254",
        "IP_SYSLOG_S": "192.168.33.1",
    }


def crear_entorno_jinja(
    template_dir: Path,
) -> Environment:
    """Crea y configura el entorno Jinja2.

    Args:
        template_dir: Directorio que contiene las plantillas.

    Returns:
        Entorno Jinja2 configurado.
    """

    if not template_dir.exists():
        raise FileNotFoundError(
            f"No existe el directorio: {template_dir}"
        )

    return Environment(
        loader=FileSystemLoader(template_dir),
        undefined=StrictUndefined,
        autoescape=False,
    )


def renderizar_configuracion(
    environment: Environment,
    template_name: str,
    valores: dict[str, object],
) -> str:
    """Renderiza una configuración Cisco.

    Args:
        environment: Entorno Jinja2.
        template_name: Nombre de la plantilla.
        valores: Variables utilizadas durante el renderizado.

    Returns:
        Configuración Cisco renderizada.

    Raises:
        TemplateRenderError: Si Jinja2 encuentra un problema.
    """

    try:
        template = environment.get_template(template_name)

        return template.render(**valores)

    except TemplateError as exc:
        raise TemplateRenderError(
            f"Error procesando {template_name}: {exc}"
        ) from exc


def guardar_configuracion(
    configuracion: str,
    hostname: str,
    output_dir: Path,
) -> Path:
    """Guarda una configuración en un archivo.

    Args:
        configuracion: Configuración Cisco.
        hostname: Nombre del dispositivo.
        output_dir: Directorio destino.

    Returns:
        Ruta del archivo creado.
    """

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    archivo = output_dir / f"{hostname}.txt"

    archivo.write_text(
        configuracion,
        encoding="utf-8",
    )

    return archivo


def generar_configuraciones(
    csv_path: Path,
    template_dir: Path,
    template_name: str,
    output_dir: Path,
) -> int:
    """Genera las configuraciones para todos los sitios.

    Args:
        csv_path: Archivo CSV.
        template_dir: Directorio de plantillas.
        template_name: Plantilla Jinja2.
        output_dir: Directorio de salida.

    Returns:
        Número de configuraciones generadas.

    Raises:
        SiteDataError: Si alguno de los registros es inválido.
    """

    sitios = cargar_sitios(csv_path)

    environment = crear_entorno_jinja(
        template_dir
    )

    generadas = 0

    for sitio in sitios:
        valores = crear_valores_jinja(sitio)

        configuracion = renderizar_configuracion(
            environment,
            template_name,
            valores,
        )

        archivo = guardar_configuracion(
            configuracion,
            str(valores["HOSTNAME"]),
            output_dir,
        )

        logger.info(
            "Configuración generada: %s",
            archivo,
        )

        generadas += 1

    return generadas
