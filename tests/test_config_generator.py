"""Pruebas unitarias del generador de configuraciones."""

import pytest

from app.config_generator import crear_valores_jinja
from app.config_generator import guardar_configuracion
from app.config_generator import renderizar_configuracion
from app.config_generator import crear_entorno_jinja
from app.exceptions import SiteDataError


@pytest.fixture
def sitio_valido():
    """Retorna información válida de un sitio."""

    return {
        "PAIS": "EC",
        "ESTADO": "PICHINCHA",
        "ID_SITIO": "001",
        "SUBRED/24": "10.10.1.0",
        "REGION": "NORTE",
    }


def test_crear_hostname(sitio_valido):
    """Verifica la creación correcta del hostname."""

    valores = crear_valores_jinja(
        sitio_valido
    )

    assert (
        valores["HOSTNAME"]
        == "ECPICHINCHARTR001"
    )


def test_calcular_ip_mgmt(sitio_valido):
    """Verifica la IP de administración."""

    valores = crear_valores_jinja(
        sitio_valido
    )

    assert valores["IP_MGMT"] == "10.10.1.254"


def test_calcular_ip_datos(sitio_valido):
    """Verifica la dirección IP de datos."""

    valores = crear_valores_jinja(
        sitio_valido
    )

    assert valores["IP_DATOS"] == "10.10.1.1"


def test_helpers(sitio_valido):
    """Comprueba los servidores DHCP helper."""

    valores = crear_valores_jinja(
        sitio_valido
    )

    assert len(valores["DATA_HELPER"]) == 3


def test_subred_invalida(sitio_valido):
    """Verifica el rechazo de una subred inválida."""

    sitio_valido["SUBRED/24"] = "999.10.1.0"

    with pytest.raises(SiteDataError):
        crear_valores_jinja(
            sitio_valido
        )


def test_campo_faltante(sitio_valido):
    """Verifica la detección de datos incompletos."""

    del sitio_valido["REGION"]

    with pytest.raises(SiteDataError):
        crear_valores_jinja(
            sitio_valido
        )


def test_render_template(
    sitio_valido,
    tmp_path,
):
    """Verifica el renderizado de una plantilla."""

    template_file = (
        tmp_path / "router.j2"
    )

    template_file.write_text(
        "hostname {{ HOSTNAME }}",
        encoding="utf-8",
    )

    environment = crear_entorno_jinja(
        tmp_path
    )

    valores = crear_valores_jinja(
        sitio_valido
    )

    config = renderizar_configuracion(
        environment,
        "router.j2",
        valores,
    )

    assert (
        "hostname ECPICHINCHARTR001"
        in config
    )


def test_guardar_configuracion(
    tmp_path,
):
    """Comprueba la escritura de configuraciones."""

    archivo = guardar_configuracion(
        configuracion="hostname RTR01\nend",
        hostname="RTR01",
        output_dir=tmp_path,
    )

    assert archivo.exists()

    assert (
        archivo.read_text(encoding="utf-8")
        == "hostname RTR01\nend"
    )
