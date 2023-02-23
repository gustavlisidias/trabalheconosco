from django import forms
from main.models import (
    ESCOLARIDADE, EXTINT, CONTRATOS, 
    Filial, Setores, Cargos, Contas, Cargos, Setores, Vagas, 
    Fase, FaseUsuario, Requisicao
)

class CadReqForm(forms.ModelForm):
    try:
        Requisicao.objects.all()
        cod = Requisicao.objects.all().last().codigo
    except:
        cod = 0

    codigo      = forms.IntegerField(widget=forms.NumberInput(attrs={'value': cod + 1}))
    gestor      = forms.ModelChoiceField(queryset=Contas.objects.all().filter(is_gestor=True))
    filial      = forms.ModelChoiceField(queryset=Filial.objects.all().order_by('cidade'))
    setor       = forms.ModelChoiceField(queryset=Setores.objects.all().order_by('nome_setor'))
    cargo       = forms.ModelChoiceField(queryset=Cargos.objects.all().order_by('nome_cargo'))
    tipo        = forms.ChoiceField(choices=EXTINT)
    tipo_vaga   = forms.ChoiceField(choices=CONTRATOS)
    ensino      = forms.ChoiceField(choices=ESCOLARIDADE)

    class Meta:
        model = Requisicao
        fields = '__all__'
        read_only_fields = ['status_a', 'usuario_a', 'data_a']
        exclude = ['is_active', 'status_b', 'usuario_b', 'data_b', 'status_c', 'usuario_c', 'data_c', 'status_d', 'usuario_d', 'data_d']


class CadVagaForm(forms.ModelForm):
    try:
        Vagas.objects.all()
        cod = Vagas.objects.all().last().codigo_vaga
    except:
        cod = 0

    data_validade   = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    codigo_vaga     = forms.IntegerField(widget=forms.NumberInput(attrs={'value': cod + 1}))
    quantidade      = forms.IntegerField(widget=forms.NumberInput(attrs={'value': 1}))
    status_vaga     = forms.BooleanField(widget=forms.CheckboxInput(attrs={'checked': True}))
    setor           = forms.ModelChoiceField(queryset=Setores.objects.all().order_by('nome_setor'))
    cargo           = forms.ModelChoiceField(queryset=Cargos.objects.all().order_by('nome_cargo'))
    regiao          = forms.ModelChoiceField(queryset=Filial.objects.all().order_by('cidade'))

    class Meta:
        model = Vagas
        fields = '__all__'


class CadSetorForm(forms.ModelForm):
    class Meta:
        model = Setores
        fields = '__all__'
        
        
class CadCargoForm(forms.ModelForm):
    class Meta:
        model = Cargos
        fields = '__all__'
        

class CadFaseForm(forms.ModelForm):
    class Meta:
        model = Fase
        fields = '__all__'
        

class CadUserFaseForm(forms.ModelForm):       
    class Meta:
        model = FaseUsuario
        fields = '__all__'