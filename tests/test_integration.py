
"""Pruebas de integración del generador de configuraciones."""

import main as main_module


def test_flujo_completo(
    tmp_path,
    monkeypatch,
) -> None:
    """Verifica el flujo CSV -> Jinja2 -> configuración Cisco."""

    docs_dir = tmp_path / "docs"

    docs_dir.mkdir()

    csv_file = (
        docs_dir / "info_sucursales.csv"
    )

    csv_file.write_text(
        (
            "PAIS,ESTADO,ID_SITIO,SUBRED/24,REGION\n"
            "EC,PICHINCHA,001,10.10.1.0,NORTE\n"
        ),
        encoding="utf-8",
    )

    template_file = (
        docs_dir / "plantilla_config.j2"
    )

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

    configs_dir = tmp_path / "configs"

    monkeypatch.setattr(
        main_module,
        "DOCS_DIR",
        docs_dir,
    )

    monkeypatch.setattr(
        main_module,
        "CSV_FILE",
        csv_file,
    )

    monkeypatch.setattr(
        main_module,
        "CONFIGS_DIR",
        configs_dir,
    )

    resultado = main_module.main()

    assert resultado == 0

    archivo = (
        configs_dir
        / "ECPICHINCHARTR001.txt"
    )

    assert archivo.exists()

    contenido = archivo.read_text(
        encoding="utf-8"
    )

    assert (
        "hostname ECPICHINCHARTR001"
        in contenido
    )

    assert "10.10.1.254" in contenido

    assert contenido.strip().endswith(
        "end"
    )
