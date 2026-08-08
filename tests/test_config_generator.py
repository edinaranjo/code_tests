"""Pruebas unitarias del generador de configuraciones."""

import pytest
from jinja2 import Environment, FileSystemLoader, StrictUndefined

<<<<<<< Updated upstream
from main import crear_config_jinja, crear_valores_jinja
=======
from app.config_generator import (
    crear_entorno_jinja,
    crear_valores_jinja,
    guardar_configuracion,
    renderizar_configuracion,
)
from app.exceptions import SiteDataError
>>>>>>> Stashed changes


@pytest.fixture
def sitio_valido() -> dict[str, str]:
    """Proporciona un registro válido para las pruebas."""

    return {
        "PAIS": "EC",
        "ESTADO": "PICHINCHA",
        "ID_SITIO": "001",
        "SUBRED/24": "10.10.1.0",
        "REGION": "NORTE",
    }


def test_crear_hostname(
    sitio_valido: dict[str, str],
) -> None:
    """Verifica la construcción del hostname."""

    valores = crear_valores_jinja(sitio_valido)

    assert valores["HOSTNAME"] == "ECPICHINCHARTR001"


def test_calcular_ip_management(
    sitio_valido: dict[str, str],
) -> None:
    """Verifica el cálculo de la IP de administración."""

    valores = crear_valores_jinja(sitio_valido)

    assert str(
        valores["IP_MGMT"]
    ) == "10.10.1.254"


def test_calcular_ip_datos(
    sitio_valido: dict[str, str],
) -> None:
    """Verifica el cálculo de la IP de datos."""

    valores = crear_valores_jinja(sitio_valido)

    assert str(
        valores["IP_DATOS"]
    ) == "10.10.1.1"


def test_data_helpers(
    sitio_valido: dict[str, str],
) -> None:
    """Verifica la lista de servidores DHCP helper."""

    valores = crear_valores_jinja(sitio_valido)

    assert valores["DATA_HELPER"] == [
        "172.18.25.1",
        "172.18.26.2",
        "172.18.27.3",
    ]


def test_region(
    sitio_valido: dict[str, str],
) -> None:
    """Verifica la región correspondiente al sitio."""

    valores = crear_valores_jinja(
        sitio_valido
    )

    assert valores["REGION"] == "NORTE"


def test_subred_invalida(
    sitio_valido: dict[str, str],
) -> None:
    """Verifica la detección de una dirección IPv4 inválida."""

    sitio_valido["SUBRED/24"] = "999.10.1.0"

<<<<<<< Updated upstream
    with pytest.raises(
        ValueError,
        match="Error procesando la subred",
    ):
        crear_valores_jinja(
            sitio_valido
        )
=======
    with pytest.raises(SiteDataError):
        crear_valores_jinja(sitio_valido)
>>>>>>> Stashed changes


def test_campo_obligatorio_inexistente(
    sitio_valido: dict[str, str],
) -> None:
    """Verifica la detección de campos obligatorios inexistentes."""

    del sitio_valido["REGION"]

<<<<<<< Updated upstream
    with pytest.raises(
        ValueError,
        match="Campo obligatorio inexistente",
    ):
        crear_valores_jinja(
            sitio_valido
        )
=======
    with pytest.raises(SiteDataError):
        crear_valores_jinja(sitio_valido)
>>>>>>> Stashed changes


def test_generar_archivo_configuracion(
    sitio_valido: dict[str, str],
    tmp_path,
) -> None:
    """Verifica el renderizado y escritura de una configuración."""

    templates_dir = tmp_path / "templates"

    templates_dir.mkdir()

<<<<<<< Updated upstream
    template_file = (
        templates_dir / "router.j2"
    )
=======
    template_file = tmp_path / "router.j2"
>>>>>>> Stashed changes

    template_file.write_text(
        (
            "hostname {{ HOSTNAME }}\n"
            "interface Loopback0\n"
            " ip address {{ IP_MGMT }} "
            "255.255.255.255\n"
            "end\n"
        ),
        encoding="utf-8",
    )

<<<<<<< Updated upstream
    environment = Environment(
        loader=FileSystemLoader(
            templates_dir
        ),
        undefined=StrictUndefined,
        autoescape=False,
    )
=======
    environment = crear_entorno_jinja(tmp_path)
>>>>>>> Stashed changes

    valores = crear_valores_jinja(sitio_valido)

    output_dir = tmp_path / "configs"

    archivo = crear_config_jinja(
        environment,
        "router.j2",
        valores,
<<<<<<< Updated upstream
        output_dir,
=======
    )

    assert "hostname ECPICHINCHARTR001" in config


def test_guardar_configuracion(
    tmp_path,
):
    """Comprueba la escritura de configuraciones."""

    archivo = guardar_configuracion(
        configuracion="hostname RTR01\nend",
        hostname="RTR01",
        output_dir=tmp_path,
>>>>>>> Stashed changes
    )

    assert archivo.exists()

<<<<<<< Updated upstream
    contenido = archivo.read_text(
        encoding="utf-8"
    )

    assert (
        "hostname ECPICHINCHARTR001"
        in contenido
    )

    assert "10.10.1.254" in contenido
=======
    assert archivo.read_text(encoding="utf-8") == "hostname RTR01\nend"
>>>>>>> Stashed changes
