"""Views for the statistics data visualization app."""
from typing import Any, Dict

from django.conf import settings
from django.http import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView

from ddionrails.data.models.variable import Variable
from ddionrails.studies.models import Study


def statistics_detail_view(
    request: HttpRequest, study: Study, plot_type: str
) -> HttpResponse:
    """Render numerical and categorical statistics views."""
    statistics_server_url = f"{request.get_host()}{settings.STATISTICS_SERVER_URL}"
    context: Dict[str, Any] = {}
    context[
        "statistics_server_url"
    ] = f"{request.scheme}://{statistics_server_url}{plot_type}/"
    context["study"] = study
    context["server_metadata"] = {
        "url": context["statistics_server_url"],
        "study": study.name,
    }
    context["variable"] = Variable.objects.select_related("dataset").get(
        id=request.GET["variable"]
    )
    return render(request, "statistics/statistics_detail.html", context=context)


class StatisticsView(TemplateView):
    """Render overview for all numerical and categorical statistics views."""

    template_name = "statistics/statistics.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context["categorical_variables"] = {}
        context["numerical_variables"] = {}
        for variable in Variable.objects.filter(statistics_data__plot_type="categorical"):
            context["categorical_variables"][
                variable.id
            ] = f"{variable.label_de}: {variable.name}"

        for variable in Variable.objects.filter(statistics_data__plot_type="numerical"):
            context["numerical_variables"][
                variable.id
            ] = f"{variable.label_de}: {variable.name}"

        return context


VARIABLES = {
    "categorical": {
        "beruf": "Berufsgruppen",
        "party": "Parteineigung",
        "religion": "Konfession",
        "plh0012_h": "Parteineigung [harmonisiert]",
        "plh0032": "Sorgen allgemeine wirtschaftliche Entwicklung",
        "plh0033": "Sorgen eigene wirtschaftliche Situation",
        "plh0034": "Sorgen Stabilitaet Finanzmaerkte",
        "plh0035": "Sorgen eigene Gesundheit",
        "plh0036": "Sorgen Umweltschutz",
        "plh0037": "Sorgen Klimawandelfolgen",
        "plh0038": "Sorgen Friedenserhaltung",
        "plh0039": "Sorgen globalen Terrorismus",
        "plh0040": "Sorgen Kriminalitaetsentwicklung in Deutschland",
        "plh0042": "Sorgen Arbeitsplatzsicherheit",
        "pli0092_h": "Aktiver Sport [harmonisiert]",
        "pli0095_h": "Mithelfen bei Freund., Verwandt. [harmonisiert]",
        "pli0096_h": (
            "Ehrenamtliche Taetigkeit in Vereinen, Verbaenden, ... [harmonisiert]"
        ),
        "pli0097_h": (
            "Beteilig. Parteien, Kommunalpolitik, Buergerinitiativen [harmonisiert]"
        ),
        "pli0098_h": "Kirchgang, Besuch religioeser Veranstaltungen [harmonisiert]",
        "plj0046": "Sorgen Zuwanderung",
        "plj0047": "Sorgen Auslaenderfeindlichkeit",
    },
    "numerical": {
        "pglabgro": "Akt. Bruttoerwerbseink.(gen) in Euro",
        "pglabnet": "Akt. Nettoerwerbseink.(gen) in Euro",
        "pgtatzeit": "Tatsächliche Arbeitszeit pro Woche",
        "pgvebzeit": "Vereinbarte Arbeitszeit pro Woche",
        "plh0164": "Zufriedenh. Schul- und Berufsausbildung",
        "plh0166": "Allg. Lebenszufriedenheit in einem Jahr",
        "plh0171": "Zufriedenheit Gesundheit",
        "plh0172": "Zufriedenheit Schlaf",
        "plh0173": "Zufriedenheit Arbeit",
        "plh0174": "Zufriedenheit HH-Taetigk.",
        "plh0175": "Zufriedenheit HH-Einkommen",
        "plh0176": "Zufriedenheit mit persoenlichem Einkommen",
        "plh0177": "Zufriedenheit Wohnung",
        "plh0178": "Zufriedenheit Freizeit",
        "plh0179": "Zufriedenheit Kinderbetreuung",
        "plh0180": "Zufriedenheit Familienleben",
        "plh0181": "Zufriedenheit Freundes-, Bekanntenkreis",
        "plh0182": "Lebenszufriedenheit gegenwaertig",
        "plh0183": "Lebenszufriedenheit in 5 Jahren",
        "y11101": "Consumer Price Index",
    },
}