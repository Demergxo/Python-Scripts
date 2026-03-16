from django import forms
from .models import Query, QueryParam


class QuerySelectForm(forms.Form):
    query = forms.ModelChoiceField(
        queryset=Query.objects.none(),
        label="Selecciona una consulta",
        empty_label="-- elige una --",
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["query"].queryset = Query.objects.filter(is_active=True).order_by("name") #type:ignore


def build_query_run_form(query: Query):
    """
    Devuelve una clase de Form dinámica para una Query concreta.
    """
    fields = {}

    for p in query.params.all(): #type:ignore
        required = p.required
        label = p.label
        initial = p.default if p.default != "" else None

        if p.param_type == QueryParam.ParamType.INT:
            field = forms.IntegerField(required=required, label=label, initial=initial)

        elif p.param_type == QueryParam.ParamType.BOOL:
            field = forms.BooleanField(required=False, label=label, initial=False)

        elif p.param_type == QueryParam.ParamType.DATE:
            field = forms.DateField(
                required=required,
                label=label,
                initial=initial,
                input_formats=["%Y-%m-%d"],
                widget=forms.DateInput(attrs={"type": "date"}),
            )

        else: # STR
            field = forms.CharField(required=required, label=label, initial=initial)

        fields[p.name] = field

    # clean cruzado (fecha_inicio <= fecha_fin)
    def clean(self):
        cleaned = super(DynamicForm, self).clean() #type:ignore
        fi = cleaned.get("fecha_inicio")
        ff = cleaned.get("fecha_fin")
        if fi is not None and ff is not None and fi > ff:
            self.add_error("fecha_fin", "La fecha fin debe ser igual o posterior a la fecha inicio.")
        return cleaned

    DynamicForm = type(
        f"QueryRunForm_{query.code}",
        (forms.Form,),
        {**fields, "clean": clean},
    )
    return DynamicForm



        