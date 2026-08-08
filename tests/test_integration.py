"""Pruebas de integración del generador."""

#from app.config_generator import generar_configuraciones


def test_generacion_completa(
    tmp_path,
):
    """Comprueba el flujo CSV -> Jinja2 -> configuración."""

    csv_file = tmp_path / "sites.csv"

    csv_file.write_text(
        (
            "PAIS,ESTADO,ID_SITIO,SUBRED/24,REGION\n"
            "EC,PICHINCHA,001,10.10.1.0,NORTE\n"
        ),
        encoding="utf-8",
    )

    templates = tmp_path / "templates"

    templates.mkdir()

    template_file = (
        templates / "router.j2"
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

    output = tmp_path / "configs"

    cantidad = generar_configuraciones(
        csv_path=csv_file,
        template_dir=templates,
        template_name="router.j2",
        output_dir=output,
    )

    assert cantidad == 1

    archivo = (
        output / "ECPICHINCHARTR001.txt"
    )

    assert archivo.exists()

    config = archivo.read_text(
        encoding="utf-8"
    )

    assert "hostname ECPICHINCHARTR001" in config
    assert "10.10.1.254" in config
    assert config.strip().endswith("end")
