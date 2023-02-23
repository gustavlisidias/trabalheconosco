from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.forms import formset_factory
from main.models import (
    Contas, Setores, DadosPessoais, Formacao, Experiencia, Idioma, Tecnologia, Complementar, Vagas, VagasUsuarios,
    Questionario, Arquivos, ImagensPerfil, Termo, Paises, Estados, Cidades, Tecnologias, Idiomas, Niveis, 
    INSPECAO, CNH, DISTANCIA, SEXO, CIVIL
)

# Configuração do WIDGET de data
class DateInput(forms.DateInput):
    input_type = 'date'
    

# Form de Registrar Conta
class RegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=60, help_text='Adicione um email válido.')
    password1 = forms.CharField(help_text='Sua senha deve conter letras, números e caracteres especiais.')
    class Meta:
        model = Contas
        fields = ("email", "username", "password1", "password2")


# Form de Autenticação de Conta
class AccountAuthenticationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        model = Contas
        fields = ('email', 'password')

    def clean(self):
        if self.is_valid():
            email = self.cleaned_data['email']
            password = self.cleaned_data['password']
            if not authenticate(email=email, password=password):
                raise forms.ValidationError("Login inválido!")


# Form de Update da Conta
class AccountUpdateForm(forms.ModelForm):
    class Meta:
        model = Contas
        fields = ('email', 'username', )

    def clean_email(self):
        if self.is_valid():
            email = self.cleaned_data['email']
            try:
                contas = Contas.objects.exclude(pk=self.instance.pk).get(email=email)
            except Contas.DoesNotExist:
                return email
            raise forms.ValidationError('Este email já foi utilizado. Por favor escolha outro.')
    
    def clean_username(self):
        if self.is_valid():
            username = self.cleaned_data['username']
            try:
                contas = Contas.objects.exclude(pk=self.instance.pk).get(username=username)
            except Contas.DoesNotExist:
                return username
            raise forms.ValidationError('Este nome já foi utilizado. Por favor escolha outro.')


# Form para Contatos Diretos
class ContatoForm(forms.Form):
    from_name = forms.CharField(required=True)
    from_email = forms.EmailField(required=True)
    from_telefone = forms.CharField()
    subject = forms.CharField(required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)
    

# Form Dados Pessoais
class DadosPessoaisForm(forms.ModelForm):  
    pais            = forms.ModelChoiceField(queryset=Paises.objects.all().order_by('name'))
    estado          = forms.ModelChoiceField(queryset=Estados.objects.filter(country=31).order_by('name'))
    cidade          = forms.ModelChoiceField(queryset=Cidades.objects.filter(country=31).order_by('name'))
    sexo            = forms.ChoiceField(required=True, choices=SEXO)
    estado_civil    = forms.ChoiceField(required=True, choices=CIVIL)

    class Meta:
        model = DadosPessoais
        fields = '__all__'
        exclude = ['usuario']
        widgets = {
            'data_nascimento': DateInput(),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(DadosPessoaisForm, self).__init__(*args, **kwargs)
        
    def save(self, commit=True):
        obj = super(DadosPessoaisForm, self).save(commit=False)
        obj.usuario = self.user
        if commit:
            obj.save()
        return obj


# Form Formacao Academica
class FormacaoForm(forms.ModelForm):
    class Meta:
        model = Formacao
        fields = '__all__'
        exclude = ['usuario']      
FormacaoFormset = formset_factory(FormacaoForm, extra=1)


# Form Experiencias Profissionais
class ExperienciaForm(forms.ModelForm):
    cargo_exp = forms.CharField(widget=forms.Textarea(attrs={"rows":4}))
    atividades_exp = forms.CharField(widget=forms.Textarea(attrs={"rows":4}))
    atuacao  = forms.ModelChoiceField(queryset=Setores.objects.all().order_by('nome_setor'))
    class Meta:
        model = Experiencia
        fields = '__all__'
        exclude = ['usuario']
        widgets = {
            'data_entrada': DateInput(),
            'data_saida': DateInput(),
        }
ExperienciaFormset = formset_factory(ExperienciaForm, extra=1)
   
    
# Form Idiomas
class IdiomaForm(forms.ModelForm):
    idioma          = forms.ModelChoiceField(queryset=Idiomas.objects.all().order_by('idioma'))      
    nivel_idioma    = forms.ModelChoiceField(queryset=Niveis.objects.all().filter(grupo__in=[2,0]).order_by('id'))      
    class Meta:
        model = Idioma
        fields = '__all__'
        exclude = ['usuario']
IdiomaFormset = formset_factory(IdiomaForm, extra=1)


# Form Tecnologias
class TecnologiaForm(forms.ModelForm):
    sistema          = forms.ModelChoiceField(queryset=Tecnologias.objects.all().order_by('tecnologia'))      
    nivel_sistema    = forms.ModelChoiceField(queryset=Niveis.objects.all().filter(grupo__in=[2,1]).order_by('id')) 
    class Meta:
        model = Tecnologia
        fields = '__all__'
        exclude = ['usuario']
TecnologiaFormset = formset_factory(TecnologiaForm, extra=1)


# Form Dados Complementares
class DadosComplementaresForm(forms.ModelForm):  
    pretensao       = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'R$'}))
    interesse1      = forms.ModelChoiceField(queryset=Setores.objects.all().order_by('nome_setor'))
    interesse2      = forms.ModelChoiceField(queryset=Setores.objects.all().order_by('nome_setor'))
    inspecao        = forms.ChoiceField(required=True, choices=INSPECAO)
    cnh             = forms.ChoiceField(required=True, choices=CNH)
    distancia       = forms.ChoiceField(required=True, choices=DISTANCIA)

    class Meta:
        model = Complementar
        fields = '__all__'
        exclude = ['usuario'] 

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(DadosComplementaresForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        obj = super(DadosComplementaresForm, self).save(commit=False)
        obj.usuario = self.user
        if commit:
            obj.save()
        return obj
    
    
# Form Questionario
class QuestionarioForm(forms.ModelForm):
    class Meta:
        model = Questionario
        fields = '__all__'
        read_only_fields = ['pontuacao_questionario', 'usuario']


# Form Arquivos
class ArquivosForm(forms.ModelForm):
    documentos = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
    class Meta:
        model = Arquivos
        fields = '__all__'
        exclude = ['usuario']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ArquivosForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        obj = super(ArquivosForm, self).save(commit=False)
        obj.usuario = self.user
        if commit:
            obj.save()
        return obj


# Form Imagem Perfil
class ImagemForm(forms.ModelForm):
    class Meta:
        model = ImagensPerfil
        fields = '__all__'
        exclude = ['usuario']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ImagemForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        obj = super(ImagemForm, self).save(commit=False)
        obj.usuario = self.user
        if commit:
            obj.save()
        return obj


# Form Vagas
class VagasForm(forms.ModelForm):
    class Meta:
        model = Vagas
        fields = '__all__'


# Form Cadastro Vagas
class VagasUsuariosForm(forms.ModelForm):
    class Meta:
        model = VagasUsuarios
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(VagasUsuariosForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        obj = super(VagasUsuariosForm, self).save(commit=False)
        obj.usuario = self.user
        if commit:
            obj.save()
        return obj
VagasUsuariosFormset = formset_factory(VagasUsuariosForm)


# Form Termo de Uso
class TermoForm(forms.ModelForm):
    class Meta:
        model = Termo
        fields = '__all__'
        exclude = ['usuario']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(TermoForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        obj = super(TermoForm, self).save(commit=False)
        obj.usuario = self.user
        if commit:
            obj.save()
        return obj