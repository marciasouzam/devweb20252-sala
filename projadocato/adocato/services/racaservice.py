
from adocato.models import Gato,Raca
from django.core.exceptions import ValidationError ''' classe fornecida pelo django; nesse projeto, usamos dicionario de erros '''
class RacaService:
   
   #metodos estaticos nao dependem do estado de instancia ou da classe
    @staticmethod 
    def buscar_raca(nome=None, disponivel=None): #INDICA QUE NAO É OBRIGATORIO
    #verifica se o gato disponivel com determinado nome existe 
        racas = Raca.objects.all()
        if nome:
            racas = racas.filter(nome__icontains=nome)
        if disponivel is not None:
            racas = racas.filter(disponivel=disponivel)
        return gatos.order_by('nome')