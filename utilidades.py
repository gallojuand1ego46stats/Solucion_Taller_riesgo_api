"""Utilidades transversales del servicio."""
import functools


def con_registro(func):
    """Registra la llamada; si falla, deja que el error se propague."""
    @functools.wraps(func)
    def envoltura(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            print(f"[registro] {func.__name__} falló: {exc}")
            raise
    return envoltura
