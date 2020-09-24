from django.http import HttpResponse
from django_weasyprint.utils import django_url_fetcher
from weasyprint import HTML


def html_to_pdf_response(html_string, pdf_filename):
    pdf_file = HTML(
        string=html_string,
        url_fetcher=django_url_fetcher,
        base_url='file://abobrinha').write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'filename="{pdf_filename}"'
    return response
