import os

from django.conf import settings


def busca_edital(nome_edital):
    """Busca o arquivo do edital e suas informações

    Args:
        nome_edital (str): O nome do arquivo do edital

    Raises:
        FileNotFoundError: Quando arquivo não encontrado
    
    Returns:
        edital_info (dict): Diciónario com informações do edital.
            conteúdo edital_info:
                content: Conteúdo do arquivo
                content_type: Tipo do conteúdo
                Content-Disposition: Disposição do conteúdo
    """
    caminho_arquivo, ext = busca_caminho_edital(nome_edital)
    try:
        with open(caminho_arquivo, 'rb') as file_:
            return {
                'content': file_.read(), 
                'content_type':f'application/{ext}',
                'Content-Disposition': f'attachment; filename={nome_edital}'
            }
    except FileNotFoundError as e:
        raise e


def busca_caminho_edital(nome_edital):
    """Busca o caminho do arquivo do edital e sua extensão.
    
    Args:
        nome_edital (str): O nome do arquivo do edital

    Returns:
        Tuple: Tuple com caminho do arquivo e sua extensão
    """
    _, ext = os.path.splitext(nome_edital)
    caminho_arquivo = os.path.join(settings.MEDIA_ROOT, nome_edital)
    return caminho_arquivo, ext