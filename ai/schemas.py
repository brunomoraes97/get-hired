from pydantic import BaseModel, Field
from typing import Annotated, List, Literal, Union

# Blocos de Construção Básicos
class Contato(BaseModel):
    tipo: str
    valor: str

class Pessoais(BaseModel):
    nome: str
    contatos: List[Contato]

class EntryWithHighlights(BaseModel):
    """Para itens como experiência, educação, projetos."""
    data: str
    titulo: str
    subtitulo: str
    local: str
    destaques: List[str]

class Category(BaseModel):
    """Para agrupar itens como em tecnologias."""
    nome: str
    itens: List[str]

# Tipos de Seção Concretos
class SectionListSimple(BaseModel):
    """Para listas simples, como Idiomas ou Interesses."""
    type: Literal["lista_simples"]
    titulo: str
    itens: List[str]

class SectionListCategorized(BaseModel):
    """Para listas categorizadas, como Competências/Tecnologias."""
    type: Literal["lista_categorizada"]
    titulo: str
    categorias: List[Category]

class SectionWithEntries(BaseModel):
    """Para seções complexas com entradas, como Experiência ou Educação."""
    type: Literal["entradas_com_destaques"]
    titulo: str
    entradas: List[EntryWithHighlights]

# Union para permitir qualquer tipo de seção na lista
AnySection = Union[SectionListSimple, SectionListCategorized, SectionWithEntries]

# Schema Principal do CV
class CV(BaseModel):
    pessoais: Pessoais
    secoes: List[Annotated[AnySection, Field(discriminator="type")]]