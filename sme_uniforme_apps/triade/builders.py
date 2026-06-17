import base64
import json
import os
import uuid

from django.utils.text import slugify

from sme_uniforme_apps.proponentes.cnpj import compact_cnpj

from .exceptions import TriadePermanentError


class TriadePayloadBuilderError(TriadePermanentError):
    pass


class TriadePayloadBuilder:
    MAX_DOCUMENT_SIZE_BYTES = 15 * 1024 * 1024
    MAX_PAYLOAD_SIZE_BYTES = 50 * 1024 * 1024

    def __init__(
        self,
        source_system,
        schema_version,
        origem_operacional="concluir-cadastro",
        fluxo="mvp_conclusao_cadastro",
    ):
        self.source_system = self._required_value(source_system, "source_system")
        self.schema_version = self._required_value(schema_version, "schema_version")
        self.origem_operacional = self._required_value(
            origem_operacional, "origem_operacional"
        )
        self.fluxo = self._required_value(fluxo, "fluxo")

    def build(self, proponente, external_batch_id, anexos=None, metadata_extra=None):
        external_batch_id = self._build_external_batch_id(external_batch_id)
        lojas = list(proponente.lojas.order_by("id"))
        primeira_loja = self._get_primeira_loja(lojas)
        documentos = self._build_documents(proponente, lojas, anexos)

        payload = {
            "source_system": self.source_system,
            "schema_version": self.schema_version,
            "external_batch_id": external_batch_id,
            "applicant": {
                "document_number": self._normalized_document_number(proponente.cnpj),
                "name": self._required_value(
                    proponente.razao_social, "proponente.razao_social"
                ),
                "fields": self._build_applicant_fields(
                    proponente, primeira_loja, lojas
                ),
            },
            "documents": documentos,
            "metadata": self._build_lote_metadata(proponente, metadata_extra),
        }

        self._validate_payload_size(payload)
        return payload

    def _build_applicant_fields(self, proponente, primeira_loja, lojas):
        return {
            "razao_social": self._required_value(
                proponente.razao_social, "proponente.razao_social"
            ),
            "cep": self._required_value(proponente.end_cep, "proponente.end_cep"),
            "endereco": self._required_value(
                proponente.end_logradouro, "proponente.end_logradouro"
            ),
            "cidade": self._required_value(
                proponente.end_cidade, "proponente.end_cidade"
            ),
            "uf": self._required_value(proponente.end_uf, "proponente.end_uf"),
            "nome_completo": self._required_value(
                proponente.responsavel, "proponente.responsavel"
            ),
            "telefone": self._required_value(
                proponente.telefone, "proponente.telefone"
            ),
            "email": self._required_value(proponente.email, "proponente.email"),
            "nome_fantasia": self._required_value(
                primeira_loja.nome_fantasia, "primeira_loja.nome_fantasia"
            ),
            "bairro": self._required_value(
                primeira_loja.bairro, "primeira_loja.bairro"
            ),
            "numero": self._required_value(
                primeira_loja.numero, "primeira_loja.numero"
            ),
            "telefone_responsavel": self._required_value(
                proponente.telefone, "proponente.telefone"
            ),
            "ponto-venda": self._build_pontos_venda(proponente, lojas),
        }

    def _build_pontos_venda(self, proponente, lojas):
        pontos_venda = []
        for loja in lojas:
            ponto_venda = {}
            campos = (
                ("nome-loja", loja.nome_fantasia),
                ("endereco", loja.endereco),
                ("numero", loja.numero),
                ("cep", loja.cep),
                ("bairro", loja.bairro),
                ("cidade", "São Paulo"),
                ("uf", "SP"),
                ("telefone", loja.telefone),
                ("site", loja.site),
            )
            for chave, valor in campos:
                valor_normalizado = self._optional_value(valor)
                if valor_normalizado:
                    ponto_venda[chave] = valor_normalizado

            if ponto_venda:
                pontos_venda.append(ponto_venda)

        return pontos_venda

    def _build_documents(self, proponente, lojas, anexos):
        anexos_ordenados = self._get_anexos(proponente, anexos)
        documentos = []
        external_document_ids = set()

        for anexo in anexos_ordenados:
            if anexo.proponente_id != proponente.id:
                raise TriadePayloadBuilderError(
                    "TRIADE payload exige anexos vinculados ao mesmo proponente do lote."
                )

            tipo_documento = anexo.tipo_documento
            if not tipo_documento or not self._optional_value(
                tipo_documento.identificador
            ):
                raise TriadePayloadBuilderError(
                    "TRIADE payload exige TipoDocumento.identificador preenchido para o anexo {}.".format(
                        anexo.uuid
                    )
                )

            external_document_id = str(anexo.uuid)
            if external_document_id in external_document_ids:
                raise TriadePayloadBuilderError(
                    "TRIADE payload exige external_document_id unico dentro do lote."
                )

            external_document_ids.add(external_document_id)
            title = self._build_document_title(anexo)
            content_data = self._build_document_content(anexo)

            documentos.append(
                {
                    "external_document_id": external_document_id,
                    "document_type": tipo_documento.identificador,
                    "title": title,
                    "content": {
                        "type": "base64",
                        "mime_type": "application/pdf",
                        "data": content_data,
                    },
                    "metadata": self._build_document_metadata(proponente, anexo),
                }
            )

        documentos.extend(
            self._build_loja_documents(proponente, lojas, external_document_ids)
        )

        return documentos

    def _build_loja_documents(self, proponente, lojas, external_document_ids):
        documentos = []
        for loja in lojas:
            for campo, prefixo_identificador in (
                ("foto_fachada", "foto-fachada"),
                ("comprovante_endereco", "comprovante-endereco"),
            ):
                arquivo = getattr(loja, campo, None)
                if not arquivo:
                    continue

                nome_fantasia_slug = slugify(loja.nome_fantasia or "")
                identificador = (
                    "{}-{}-{}".format(
                        prefixo_identificador, nome_fantasia_slug, loja.id
                    )
                    if nome_fantasia_slug
                    else "{}-{}".format(prefixo_identificador, loja.id)
                )
                external_document_id = self._build_loja_external_document_id(
                    loja, campo
                )

                if external_document_id in external_document_ids:
                    raise TriadePayloadBuilderError(
                        "TRIADE payload exige external_document_id unico dentro do lote."
                    )
                external_document_ids.add(external_document_id)

                title = self._build_loja_document_title(arquivo, loja, campo)
                mime_type = self._resolve_mime_type(arquivo)
                content_data = self._build_loja_document_content(
                    arquivo, loja, campo
                )

                documentos.append(
                    {
                        "external_document_id": external_document_id,
                        "document_type": identificador,
                        "title": title,
                        "content": {
                            "type": "base64",
                            "mime_type": mime_type,
                            "data": content_data,
                        },
                        "metadata": self._build_loja_document_metadata(
                            proponente, loja, campo, identificador
                        ),
                    }
                )

        return documentos

    @staticmethod
    def _build_loja_external_document_id(loja, campo):
        return str(uuid.uuid5(uuid.UUID(str(loja.uuid)), campo))

    def _build_document_metadata(self, proponente, anexo):
        metadata = {
            "anexo_uuid": str(anexo.uuid),
            "proponente_uuid": str(proponente.uuid),
            "tipo_documento_id": anexo.tipo_documento_id,
            "tipo_documento_identificador": anexo.tipo_documento.identificador,
        }

        tipo_documento_nome = self._optional_value(anexo.tipo_documento.nome)
        if tipo_documento_nome:
            metadata["tipo_documento_nome"] = tipo_documento_nome

        if anexo.data_validade:
            metadata["data_validade"] = anexo.data_validade.isoformat()

        return metadata

    def _build_lote_metadata(self, proponente, metadata_extra):
        metadata = dict(metadata_extra or {})
        metadata.update(
            {
                "proponente_uuid": str(proponente.uuid),
                "protocolo": proponente.protocolo,
                "status_atual_proponente": proponente.status,
                "origem_operacional": self.origem_operacional,
                "fluxo": self.fluxo,
            }
        )
        return metadata

    def _build_document_title(self, anexo):
        nome_arquivo = ""
        if anexo.arquivo:
            nome_arquivo = os.path.basename(anexo.arquivo.name or "")

        if not nome_arquivo:
            raise TriadePayloadBuilderError(
                "TRIADE payload exige arquivo valido para o anexo {}.".format(
                    anexo.uuid
                )
            )

        return nome_arquivo

    def _build_document_content(self, anexo):
        if not anexo.arquivo:
            raise TriadePayloadBuilderError(
                "TRIADE payload exige arquivo valido para o anexo {}.".format(
                    anexo.uuid
                )
            )

        try:
            anexo.arquivo.open("rb")
            raw_content = anexo.arquivo.read()
        finally:
            anexo.arquivo.close()

        if not raw_content:
            raise TriadePayloadBuilderError(
                "TRIADE payload exige arquivo com conteudo para o anexo {}.".format(
                    anexo.uuid
                )
            )

        document_size = len(raw_content)
        if document_size > self.MAX_DOCUMENT_SIZE_BYTES:
            raise TriadePayloadBuilderError(
                "TRIADE payload excede o limite de 15 MiB para o anexo {}.".format(
                    anexo.uuid
                )
            )

        return base64.b64encode(raw_content).decode("ascii")

    def _build_loja_document_title(self, arquivo, loja, campo):
        nome_arquivo = os.path.basename(arquivo.name or "")
        if not nome_arquivo:
            raise TriadePayloadBuilderError(
                "TRIADE payload exige arquivo valido para o campo {} da loja {}.".format(
                    campo, loja.uuid
                )
            )
        return nome_arquivo

    def _build_loja_document_content(self, arquivo, loja, campo):
        try:
            arquivo.open("rb")
            raw_content = arquivo.read()
        finally:
            arquivo.close()

        if not raw_content:
            raise TriadePayloadBuilderError(
                "TRIADE payload exige arquivo com conteudo para o campo {} da loja {}.".format(
                    campo, loja.uuid
                )
            )

        document_size = len(raw_content)
        if document_size > self.MAX_DOCUMENT_SIZE_BYTES:
            raise TriadePayloadBuilderError(
                "TRIADE payload excede o limite de 15 MiB para o campo {} da loja {}.".format(
                    campo, loja.uuid
                )
            )

        return base64.b64encode(raw_content).decode("ascii")

    def _build_loja_document_metadata(self, proponente, loja, campo, identificador):
        nome_fantasia = self._optional_value(loja.nome_fantasia) or ""
        return {
            "loja_uuid": str(loja.uuid),
            "loja_id": loja.id,
            "loja_nome_fantasia": nome_fantasia,
            "campo_loja": campo,
            "proponente_uuid": str(proponente.uuid),
            "tipo_documento_identificador": identificador,
        }

    def _resolve_mime_type(self, arquivo):
        nome_arquivo = (arquivo.name or "").lower()
        if nome_arquivo.endswith(".png"):
            return "image/png"
        if nome_arquivo.endswith((".jpg", ".jpeg")):
            return "image/jpeg"
        if nome_arquivo.endswith(".pdf"):
            return "application/pdf"
        return "application/octet-stream"

    def _get_anexos(self, proponente, anexos):
        if anexos is None:
            anexos = proponente.anexos.select_related("tipo_documento").order_by("id")

        anexos_ordenados = sorted(
            list(anexos), key=lambda anexo: ((anexo.id or 0), str(anexo.uuid))
        )
        if not anexos_ordenados:
            raise TriadePayloadBuilderError(
                "TRIADE payload exige ao menos um anexo para envio."
            )

        return anexos_ordenados

    def _get_primeira_loja(self, lojas):
        if not lojas:
            raise TriadePayloadBuilderError(
                "TRIADE payload exige ao menos uma loja cadastrada para o proponente."
            )

        return lojas[0]

    def _build_external_batch_id(self, external_batch_id):
        external_batch_id = self._required_value(external_batch_id, "external_batch_id")
        if len(external_batch_id) > 128:
            raise TriadePayloadBuilderError(
                "TRIADE payload exige external_batch_id com no maximo 128 caracteres."
            )

        return external_batch_id

    def _normalized_document_number(self, cnpj):
        cnpj = self._required_value(cnpj, "proponente.cnpj")
        normalized = compact_cnpj(cnpj)
        if not normalized:
            raise TriadePayloadBuilderError(
                "TRIADE payload exige proponente.cnpj valido para envio."
            )
        return normalized

    def _validate_payload_size(self, payload):
        payload_size = len(
            json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode(
                "utf-8"
            )
        )
        if payload_size > self.MAX_PAYLOAD_SIZE_BYTES:
            raise TriadePayloadBuilderError(
                "TRIADE payload excede o limite de 50 MiB do lote."
            )

    def _required_value(self, value, field_name):
        normalized_value = self._optional_value(value)
        if not normalized_value:
            raise TriadePayloadBuilderError(
                "TRIADE payload exige o campo {} preenchido.".format(field_name)
            )
        return normalized_value

    def _optional_value(self, value):
        if value is None:
            return None

        normalized_value = str(value).strip()
        return normalized_value or None
