from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from ckeditor.fields import RichTextField
from django.db import models
import datetime, re

PRIORIDADE = [
    ("Baixa", "Baixa"),
    ("Média", "Média"), 
    ("Alta", "Alta"),
    ("Urgente", "Urgente")
]

CONTRATOS = [
    ("Aprendiz", "Aprendiz"),
    ("CLT", "CLT"),
    ("Estágio", "Estágio"),
    ("Temporario", "Temporario"),    
]

ESCOLARIDADE = [
    ("Ensino Médio", "Ensino Médio"),
    ("Ensino Técnico", "Ensino Técnico"),
    ("Ensino Superior", "Ensino Superior"),
    ("Pós Graduação", "Pós Graduação"),
    ("Mestrado", "Mestrado"),
    ("Doutorado", "Doutorado"),
]

CNH = [
    ("Não Possuo", "Não Possuo"),
    ("A", "A"),
    ("B", "B"),
    ("C", "C"),
    ("D", "D"),
    ("E", "E"),
]

SEXO = [
    ("Feminino", "Feminino"),
    ("Masculino", "Masculino"),
    ("Prefiro não declarar", "Prefiro não declarar"),
]

CIVIL = [
    ("Casado(a)", "Casado(a)"),
    ("Divorciado(a)", "Divorciado(a)"),
    ("Solteiro(a)", "Solteiro(a)"),
    ("Viúvo(a)", "Viúvo(a)"),
]

INSPECAO = [
    ("Facebook", "Facebook"),
    ("Indicação", "Indicação"),
    ("LinkedIn", "LinkedIn"),
    ("Site", "Site"),
    ("Outros", "Outros"),
]

FORMACAO = [
    ("Em Andamento", "Em Andamento"),
    ("Concluído", "Concluído"),
    ("Trancado", "Trancado"),
]

DISTANCIA = [
    ("50km ou menos", "50km ou menos"),
    ("50km - 100km", "50km - 100km"),
    ("100km - 150km", "100km - 150km"),
    ("150km - 200km", "150km - 200km"),
    ("200km ou mais", "200km ou mais"),
]

EXTINT = [
    ('Interno', 'Interno'),
    ('Externo', 'Externo'),
    ('Interno/Externo', 'Interno/Externo'),
]


def local_upload(instance, filename):
    file_path = 'profile/{usuario}/{data_envio}__imagem__{filename}'.format(
	    usuario=(instance.usuario.email), data_envio=datetime.date.today(), filename=re.sub('[^A-Za-z0-9.]+', '', filename))
    return file_path


def doc_upload(instance, filename):
	file_path = 'documentos/{usuario}/{data_envio}__documento__{filename}'.format(
		usuario=(instance.usuario.email), data_envio=datetime.date.today(), filename=re.sub('[^A-Za-z0-9.]+', '', filename))
	return file_path


class MyAccountManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError("O usuário deve conter um endereço de e-mail.")
        if not username:
            raise ValueError("O usuário deve conter um nome.")

        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            username=username,
        )
        user.is_admin = True
        user.is_interno = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Contas(AbstractBaseUser, PermissionsMixin):
    email               = models.EmailField(verbose_name="email", max_length=60, unique=True)
    username            = models.CharField(max_length=30, unique=True)
    data_inscricao      = models.DateTimeField(verbose_name='Data de Inscrição', auto_now_add=True)
    ultimo_login        = models.DateTimeField(verbose_name='Último Login', auto_now=True)
    is_admin            = models.BooleanField(default=False)
    is_active           = models.BooleanField(default=True)
    is_rh               = models.BooleanField(default=False)
    is_superuser        = models.BooleanField(default=False)
    is_interno          = models.BooleanField(default=False)
    is_gestor           = models.BooleanField(default=False)
    is_diretor          = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = MyAccountManager()
        
    def __str__(self):
        try:
            DadosPessoais.objects.get(usuario=self.id)
            q = DadosPessoais.objects.get(usuario=self.id)
            nome = q.nome_completo
            return nome
        except DadosPessoais.DoesNotExist:
            return self.username

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perm(self, app_label):
        return True
    
    class Meta:
        verbose_name = "Conta"
        verbose_name_plural = "Contas"


class Filial(models.Model):
    nome                       = models.CharField(max_length=32)           
    razao                      = models.CharField(max_length=191)  
    cnpj                       = models.CharField(max_length=32)  
    cidade                     = models.CharField(max_length=32)  
    endereco                   = models.CharField(max_length=191)  
    cep                        = models.CharField(max_length=32)  

    def __str__(self):
        return self.cidade
    
    class Meta:
        verbose_name = "Filial"
        verbose_name_plural = "Filiais"


class Cargos(models.Model):
    nome_cargo                 = models.CharField(max_length=64, verbose_name="Cargo")
    descricao_cargo            = models.CharField(max_length=64, null=True, blank=True, verbose_name="Descrição Cargo")

    def __str__(self):
        return self.nome_cargo
    
    class Meta:
        verbose_name = "Cargo"
        verbose_name_plural = "Cadastros de Cargos" 


class Setores(models.Model):
    nome_setor                 = models.CharField(max_length=64, verbose_name="Setor")
    descricao_setor            = models.CharField(max_length=64, null=True, blank=True, verbose_name="Descrição Setor")

    def __str__(self):
        return self.nome_setor
    
    class Meta:
        verbose_name = "Setor"
        verbose_name_plural = "Cadastros de Setores" 


class Niveis(models.Model):
    nivel                   = models.CharField(max_length=32)
    grupo                   = models.IntegerField()

    def __str__(self):
        return self.nivel
    
    class Meta:
        verbose_name = "Nível"
        verbose_name_plural = "Níveis" 


class Idiomas(models.Model):
    idioma                  = models.CharField(max_length=32)
    grupo                   = models.IntegerField()

    def __str__(self):
        return self.idioma
    
    class Meta:
        verbose_name = "Idioma"
        verbose_name_plural = "Idiomas" 


class Tecnologias(models.Model):
    tecnologia              = models.CharField(max_length=32)
    grupo                   = models.IntegerField()

    def __str__(self):
        return self.tecnologia
    
    class Meta:
        verbose_name = "Tecnologia"
        verbose_name_plural = "Tecnologias" 


class Paises(models.Model):
    name	                = models.CharField(max_length=255, verbose_name="Pais")
    iso3	                = models.CharField(max_length=255, verbose_name="ISO3")
    numeric_code	        = models.IntegerField(verbose_name="Codigo")
    iso2	                = models.CharField(max_length=255, verbose_name="ISO2")
    phonecode	            = models.CharField(max_length=191, verbose_name="Código Postal")
    capital	                = models.CharField(max_length=255, verbose_name="Capital")
    currency	            = models.CharField(max_length=255, verbose_name="Moeda")
    currency_name	        = models.CharField(max_length=255, verbose_name="Nome da Moeda")
    currency_symbol		    = models.CharField(max_length=255, verbose_name="Simbolo da Moeda")	
    tld	                    = models.CharField(max_length=255)
    native	                = models.CharField(max_length=255, null=True)
    region	                = models.CharField(max_length=255, verbose_name="Regiao")
    subregion	            = models.CharField(max_length=255, verbose_name="Subregiao")
    timezones               = models.TextField()
    translations            = models.TextField()
    latitude	            = models.DecimalField(max_digits=12, decimal_places=8, null=True, verbose_name="Latitude")
    longitude               = models.DecimalField(max_digits=12, decimal_places=8, null=True, verbose_name="Longitude")
    emoji                   = models.CharField(max_length=191, verbose_name="emoji")    # ascii
    emojiU                  = models.CharField(max_length=191, verbose_name="emojiU")
    created_at              = models.DateTimeField(verbose_name="Data Criacao")
    updated_at              = models.DateTimeField(verbose_name="Data Modificacao")
    flag                    = models.BooleanField(default=True, verbose_name="Flag")
    wikiDataId              = models.CharField(max_length=255, null=True, verbose_name="WikiDataId")

    def __str__(self):
        return str(self.name)
    
    class Meta:
        verbose_name = "País"
        verbose_name_plural = "Países"


class Estados(models.Model):
    name	                = models.CharField(max_length=255, verbose_name="Nome Cidade")
    country	                = models.ForeignKey(Paises, on_delete=models.CASCADE)
    country_code            = models.CharField(max_length=255, verbose_name="Cod Pais")
    fips_code               = models.CharField(max_length=255, null=True, verbose_name="FIPS")
    iso2                    = models.CharField(max_length=255, verbose_name="ISO2")
    typ                     = models.CharField(max_length=191, null=True, verbose_name="Type")
    latitude	            = models.DecimalField(max_digits=12, decimal_places=8, null=True, verbose_name="Latitude")
    longitude               = models.DecimalField(max_digits=12, decimal_places=8, null=True, verbose_name="Longitude")
    created_at              = models.DateTimeField(verbose_name="Data Criacao")
    updated_at              = models.DateTimeField(verbose_name="Data Modificacao")
    flag                    = models.BooleanField(default=True, verbose_name="Flag")
    wikiDataId              = models.CharField(max_length=255, null=True, verbose_name="WikiDataId")

    def __str__(self):
        return str(self.name)
    
    class Meta:
        verbose_name = "Estado"
        verbose_name_plural = "Estados" 


class Cidades(models.Model):
    name	                = models.CharField(max_length=255, verbose_name="Nome Cidade")
    state	                = models.ForeignKey(Estados, on_delete=models.CASCADE)
    state_code	            = models.CharField(max_length=255, verbose_name="Cod Estado")
    country	                = models.ForeignKey(Paises, on_delete=models.CASCADE)
    country_code            = models.CharField(max_length=255, verbose_name="Cod Pais")
    latitude	            = models.DecimalField(max_digits=12, decimal_places=8, null=True, verbose_name="Latitude")
    longitude               = models.DecimalField(max_digits=12, decimal_places=8, null=True, verbose_name="Longitude")
    created_at              = models.DateTimeField(verbose_name="Data Criacao")
    updated_at              = models.DateTimeField(verbose_name="Data Modificacao")
    flag                    = models.BooleanField(default=True, verbose_name="Flag")
    wikiDataId              = models.CharField(max_length=255, null=True, verbose_name="WikiDataId")

    def __str__(self):
        return str(self.name)
    
    class Meta:
        verbose_name = "Cidade"
        verbose_name_plural = "Cidades" 


class DadosPessoais(models.Model):
    usuario                 = models.ForeignKey(Contas, on_delete=models.CASCADE)
    nome_completo           = models.CharField(max_length=200, verbose_name="Nome Completo")
    email                   = models.EmailField(max_length=200, verbose_name="Email")
    cpf                     = models.CharField(max_length=32, verbose_name="CPF")
    rg                      = models.CharField(max_length=32, verbose_name="RG")
    data_nascimento         = models.DateField(verbose_name="Data Nascimento")
    sexo                    = models.CharField(max_length=32, choices=SEXO, verbose_name="Gênero")
    estado_civil            = models.CharField(max_length=32, choices=CIVIL, verbose_name="Estado Civil")
    pais                    = models.ForeignKey(Paises, on_delete=models.CASCADE)
    estado                  = models.ForeignKey(Estados, on_delete=models.CASCADE)
    cidade                  = models.ForeignKey(Cidades, on_delete=models.CASCADE, null=True)
    cep                     = models.CharField(max_length=32, verbose_name="Código Postal")
    bairro                  = models.CharField(max_length=200, verbose_name="Bairro", null=True, blank=True)
    endereco                = models.CharField(max_length=200, verbose_name="Endereço", null=True, blank=True)
    numero                  = models.CharField(max_length=32, verbose_name="Número", null=True, blank=True)
    complemento             = models.CharField(max_length=200, verbose_name="Complemento", null=True,  blank=True)
    telefone                = models.CharField(max_length=32, null=True, blank=True)
    celular                 = models.CharField(max_length=32)
    data_cadastro           = models.DateTimeField(verbose_name='Data de Cadastro do Currículo', auto_now_add=True)
    
    def __str__(self):
        return self.nome_completo
    
    class Meta:
        verbose_name = "Currículo"
        verbose_name_plural = "Currículos"
    

class Formacao(models.Model):
    usuario                 = models.ForeignKey(Contas, on_delete=models.CASCADE, null=True, blank=True,)
    escolaridade            = models.CharField(max_length=32, null=True, blank=True, choices=ESCOLARIDADE,verbose_name="Nível de Escolaridade")
    instituicao             = models.CharField(max_length=200, null=True, blank=True, verbose_name="Instituição de Ensino")
    curso                   = models.CharField(max_length=200, null=True, blank=True, verbose_name="Curso")
    status_formacao         = models.CharField(max_length=32, null=True, blank=True, choices=FORMACAO, verbose_name="Status")

    def __str__(self):
        return str(self.usuario) + ' - ' + self.instituicao

    class Meta:
        verbose_name = "Formações Acadêmcias do Usuário"
        verbose_name_plural = "Formações Acadêmcias"


class Experiencia(models.Model):
    usuario                 = models.ForeignKey(Contas, on_delete=models.CASCADE, null=True, blank=True)
    empresa                 = models.CharField(max_length=200, null=True, blank=True, verbose_name="Organização")
    data_entrada            = models.DateField(null=True, blank=True, verbose_name="Data de Entrada")
    data_saida              = models.DateField(null=True, blank=True, verbose_name="Data de Saída")
    atuacao                 = models.ForeignKey(Setores, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Area de Atuação")
    cargo_exp               = models.TextField(null=True, blank=True, verbose_name="Cargo")
    atividades_exp          = models.TextField(null=True, blank=True, verbose_name="Atvididades")

    def __str__(self):
        return str(self.usuario) + ' - ' + self.empresa

    class Meta:
        verbose_name = "Experiências Profissional do Usuário"
        verbose_name_plural = "Experiências Profissionais"


class Idioma(models.Model):
    usuario                 = models.ForeignKey(Contas, on_delete=models.CASCADE)
    idioma                  = models.ForeignKey(Idiomas, on_delete=models.CASCADE, related_name="idioma_usuario")
    nivel_idioma            = models.ForeignKey(Niveis, on_delete=models.CASCADE, related_name="nivel_idioma_usuario")

    def __str__(self):
        return str(self.usuario) + ' - ' + self.idioma.idioma

    class Meta:
        verbose_name = "Idiomas do Usuário"
        verbose_name_plural = "Idiomas"    


class Tecnologia(models.Model):
    usuario                 = models.ForeignKey(Contas, on_delete=models.CASCADE)
    sistema                 = models.ForeignKey(Tecnologias, on_delete=models.CASCADE, related_name="tecnologia_usuario")
    nivel_sistema           = models.ForeignKey(Niveis, on_delete=models.CASCADE, related_name="nivel_tecnologia_usuario")

    def __str__(self):
        return str(self.usuario) + ' - ' + self.sistema.tecnologia

    class Meta:
        verbose_name = "Conhecimento Tecnológico do Usuário"
        verbose_name_plural = "Conhecimentos Tecnológico"


class Complementar(models.Model):
    usuario                 = models.ForeignKey(Contas, on_delete=models.CASCADE)
    primeiro_emprego        = models.BooleanField(default=False, verbose_name="Primeiro Emprego")
    deficiencia             = models.BooleanField(default=False, verbose_name="Possuo Deficiência")   
    disponivel_viagem       = models.BooleanField(default=False, verbose_name="Disponível para Viagem")
    pretensao               = models.CharField(max_length=32, null=True, blank=True, verbose_name="Pretensão Salarial")
    cnh                     = models.CharField(max_length=32, choices=CNH, verbose_name="CNH")
    inspecao                = models.CharField(max_length=32, choices=INSPECAO, verbose_name="Como Nos Conheceu")
    interesse1              = models.ForeignKey(Setores, on_delete=models.CASCADE, verbose_name="Área de Interesse (1)", related_name='primeiro_interesse')
    interesse2              = models.ForeignKey(Setores, on_delete=models.CASCADE, verbose_name="Área de Interesse (2)", related_name='segundo_interesse') 
    facebook                = models.CharField(max_length=200, null=True, blank=True, verbose_name="Facebook")
    linkedin                = models.CharField(max_length=200, null=True, blank=True, verbose_name="LinkedIn")
    distancia               = models.CharField(max_length=32, choices=DISTANCIA, verbose_name="Qual a distância entre você e nossa matriz?")
                                                                                                            

    def __str__(self):
        return str(self.usuario) + ' - ' + self.inspecao
    
    class Meta:
        verbose_name = "Dados Complementares do Usuário"
        verbose_name_plural = "Dados Complementares"


class Vagas(models.Model):
    codigo_vaga             = models.IntegerField(unique=True, verbose_name="Código da Vaga")
    status_vaga             = models.BooleanField(default=True, verbose_name="Status da Vaga")
    prioridade              = models.CharField(max_length=32, choices=PRIORIDADE, verbose_name="Urgência da Vaga")
    data_validade           = models.DateField(verbose_name="Data de Encerramento")
    cargo                   = models.ForeignKey(Cargos, on_delete=models.CASCADE, verbose_name="Cargo")
    setor                   = models.ForeignKey(Setores, on_delete=models.CASCADE, verbose_name="Setor")
    quantidade              = models.IntegerField(verbose_name="Quantidade de Vagas")
    jornada                 = models.CharField(max_length=32, default="07:30 às 17:30", verbose_name="Jornada de Trabalho")
    ensino                  = models.CharField(max_length=32, choices=ESCOLARIDADE, verbose_name="Nível de Escolaridade") 
    contratacao             = models.CharField(max_length=32, choices=CONTRATOS, verbose_name="Tipo de Contratação")
    regiao                  = models.ForeignKey(Filial, on_delete=models.CASCADE, verbose_name="Filial")
    atividades              = RichTextField(max_length=1024, verbose_name="Principais Atividades")
    qualificacao            = RichTextField(max_length=1024, verbose_name="Requisitos")
    descricao               = RichTextField(max_length=1024, verbose_name="Observações")
    
    def __str__(self):
        return str(self.codigo_vaga) + ' | ' + self.cargo.nome_cargo + ' - ' + self.setor.nome_setor

    class Meta:
        verbose_name = "Vaga"
        verbose_name_plural = "Cadastro de Vagas"


class VagasUsuarios(models.Model):
    usuario                 = models.ForeignKey(Contas, on_delete=models.CASCADE)
    vaga                    = models.ForeignKey(Vagas, on_delete=models.CASCADE)
    status_cadastro         = models.BooleanField(default=False, verbose_name="Status de Cadastro")
    pontuacao_vaga          = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Pontuacao da Vaga")
    data_cadastro           = models.DateTimeField(verbose_name='Data de Cadastro', auto_now_add=True)
    is_active               = models.BooleanField(default=True, verbose_name="Ativo")

    def __str__(self):
        return self.usuario.username + ' | ' + self.vaga.cargo.nome_cargo + ' - ' + self.vaga.setor.nome_setor
    
    class Meta:
        verbose_name = "Cadastro"
        verbose_name_plural = "Apuração de Cadastros"


class Questionario(models.Model):
    usuario                 = models.ForeignKey(Contas, on_delete=models.CASCADE)
    pergunta1               = models.TextField(verbose_name="Descreva como é um bom lugar para se trabalhar")
    pergunta2               = models.TextField(verbose_name="Você prefere trabalhar sozinho ou em equipe?")
    pergunta3               = models.TextField(verbose_name="Qual foi sua maior conquista até hoje (pessoal ou profissional)?")
    pergunta4               = models.TextField(verbose_name="Qual o seu maior sonho?")
    pergunta5               = models.TextField(verbose_name="Por que deseja trabalhar conosco?")
    pontuacao_questionario  = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,verbose_name="Pontuacao do Questionário")
    data_cadastro           = models.DateTimeField(verbose_name='Data de Cadastro do Questionario', auto_now_add=True)
    
    def __str__(self):
        return self.usuario.username
    
    class Meta:
        verbose_name = "Questionário"
        verbose_name_plural = "Apuração de Questionários"
    

class Arquivos(models.Model):
    usuario                 = models.ForeignKey(Contas, on_delete=models.CASCADE, null=True, blank=True)
    documentos              = models.FileField(upload_to=doc_upload, null=True, blank=True, verbose_name="Documentos")
    data_envio              = models.DateTimeField(verbose_name='Data de Envio dos Documentos', auto_now_add=True)
    
    def __str__(self):
        return str(self.usuario)
    
    class Meta:
        verbose_name = "Documento"
        verbose_name_plural = "Apuração de Documentos"    
        
        
class ImagensPerfil(models.Model):
    usuario                 = models.ForeignKey(Contas, on_delete=models.PROTECT, null=True, blank=True)
    imagem                  = models.ImageField(upload_to=local_upload, null=True, blank=True, verbose_name="Alterar Imagem")
    
    def __str__(self):
        return str(self.usuario)
    
    class Meta:
        verbose_name = "Imagem de Perfil"
        verbose_name_plural = "Imagens de Perfil"
        

class Termo(models.Model):
    usuario                   = models.ForeignKey(Contas, on_delete=models.CASCADE)
    status_termo              = models.BooleanField(default=True, verbose_name="Status do Termo")
    data_termo                = models.DateTimeField(verbose_name='Data de Aceite', auto_now_add=True)

    def __str__(self):
        return self.usuario.username
    
    class Meta:
        verbose_name = "Termo de Responsabilidade e Condição de Uso"
        verbose_name_plural = "Termos de Responsabilidade e Condição de Uso" 
        

class Fase(models.Model):
    fase                       = models.CharField(max_length=128, verbose_name="Fase")
    descricao_fase             = models.TextField(null=True, blank=True, verbose_name="Descrição Fase")

    def __str__(self):
        return self.fase
    
    class Meta:
        verbose_name = "Fases"
        verbose_name_plural = "Cadastros de Fases" 
        
        
class FaseUsuario(models.Model):
    usuario                   = models.ForeignKey(Contas, on_delete=models.CASCADE)
    fase                      = models.ForeignKey(Fase, on_delete=models.CASCADE, verbose_name="Fase")
    vaga                      = models.ForeignKey(Vagas, on_delete=models.CASCADE, verbose_name="Vaga", null=True, blank=True)
    observacao                = RichTextField(max_length=10240, verbose_name="Observações", null=True, blank=True)
    data_cadastro             = models.DateField(verbose_name='Data de Cadastro da Fase', auto_now_add=True)

    def __str__(self):
        return str(self.fase) + ' - ' + str(self.usuario.username)
        
    class Meta:
        verbose_name = "Fase do Processo"
        verbose_name_plural = "Fases dos Processos" 


class Requisicao(models.Model):
    codigo                  = models.IntegerField()
    filial                  = models.ForeignKey(Filial, on_delete=models.CASCADE)
    setor                   = models.ForeignKey(Setores, on_delete=models.CASCADE)
    cargo                   = models.ForeignKey(Cargos, on_delete=models.CASCADE)
    salario                 = models.IntegerField()
    gestor                  = models.ForeignKey(Contas, on_delete=models.CASCADE, null=True, blank=True, related_name="gestor")
    ensino                  = models.CharField(max_length=32, choices=ESCOLARIDADE)
    tipo                    = models.CharField(max_length=32, choices=EXTINT)
    tipo_vaga               = models.CharField(max_length=32, choices=CONTRATOS)
    requisitos              = RichTextField(max_length=10240, null=True, blank=True)
    atividades              = RichTextField(max_length=10240, null=True, blank=True)
    habilidades             = RichTextField(max_length=10240, null=True, blank=True)
    ferramentas             = RichTextField(max_length=10240, null=True, blank=True)
    recrutamento            = RichTextField(max_length=10240, null=True, blank=True)
    informacoes             = RichTextField(max_length=10240, null=True, blank=True)
    status_a                = models.BooleanField(default=True)
    usuario_a               = models.ForeignKey(Contas, on_delete=models.CASCADE, related_name="requisitante")
    data_a                  = models.DateField(auto_now_add=True)
    status_b                = models.BooleanField(default=False, null=True, blank=True)
    usuario_b               = models.ForeignKey(Contas, on_delete=models.CASCADE, null=True, blank=True, related_name="recursos_humanos")
    data_b                  = models.DateField(null=True, blank=True)
    status_c                = models.BooleanField(default=False)
    usuario_c               = models.ForeignKey(Contas, on_delete=models.CASCADE, null=True, blank=True, related_name="gerente")
    data_c                  = models.DateField(null=True, blank=True)
    status_d                = models.BooleanField(default=False)
    usuario_d               = models.ForeignKey(Contas, on_delete=models.CASCADE, null=True, blank=True, related_name="diretor")
    data_d                  = models.DateField(null=True, blank=True)
    is_active               = models.BooleanField(default=True)

    def __str__(self):
        return 'Requisicao: ' + str(self.codigo)
        
    class Meta:
        verbose_name = "Requisição de Vaga"
        verbose_name_plural = "Requisições de Vagas" 