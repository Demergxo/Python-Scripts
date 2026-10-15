from django import forms
from .data import PERIODS, STATES


class Filters(forms.Form):
    period = forms.ChoiceField(
        label="Fecha de carga",
        required=False,
        choices=[("", "Todas")] + [(v, v) for v in PERIODS],
        initial="Hoy",
    )
    status = forms.ChoiceField(
        label="Situación",
        required=False,
        choices=[("", "Todas"), ("Abierto", "Abierto"), ("Cerrado", "Cerrado")],
        initial="Abierto",
    )
    state = forms.ChoiceField(
        label="Estado XGA",
        required=False,
        choices=[("", "Todos")] + [(v, v) for v in STATES],
    )
    albaran = forms.CharField(label="Albarán", required=False, max_length=100)
    extraccion = forms.CharField(label="Extracción", required=False, max_length=100)
    expediente = forms.CharField(label="Expediente", required=False, max_length=100)
    cliente = forms.CharField(label="Cliente", required=False, max_length=100)
    muelle = forms.CharField(label="Muelle", required=False, max_length=100)
