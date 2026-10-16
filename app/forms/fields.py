from wtforms import StringField


class TrimmedStringField(StringField):
    """StringField que elimina los espacios al inicio y al final.

    Evita que un correo copiado con espacios falle la validación
    del campo antes de que la ruta llegue a normalizarlo.
    """

    def process_formdata(self, valuelist):
        super().process_formdata(valuelist)

        if isinstance(self.data, str):
            self.data = self.data.strip()
