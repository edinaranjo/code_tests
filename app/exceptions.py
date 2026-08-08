"""Excepciones personalizadas de la aplicación."""


class ConfigurationError(Exception):
    """Error base relacionado con la generación de configuraciones."""


class SiteDataError(ConfigurationError):
    """Indica datos inválidos correspondientes a un sitio."""


class TemplateRenderError(ConfigurationError):
    """Indica un problema durante el procesamiento de la plantilla."""
