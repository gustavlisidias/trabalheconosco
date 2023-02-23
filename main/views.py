from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.db.models import Q
from django.contrib import messages

from main.models import (
    DadosPessoais, Formacao, Experiencia, Idioma, Tecnologia, Complementar,
    Vagas, VagasUsuarios, Questionario, Arquivos, ImagensPerfil, Termo, Paises, Estados, Cidades
)
from main.forms import (
    RegistrationForm, AccountAuthenticationForm, ContatoForm, ArquivosForm, ImagemForm, QuestionarioForm, TermoForm, VagasUsuariosForm, 
    VagasUsuariosFormset, DadosPessoaisForm, FormacaoForm, FormacaoFormset, ExperienciaForm, ExperienciaFormset, IdiomaForm, 
    IdiomaFormset, TecnologiaForm, TecnologiaFormset, DadosComplementaresForm
)

import datetime


# Cadastro de Dados Pessoais    
def DadosPessoaisView(request):
    if not request.user.is_authenticated:
        return redirect("entrar")
    
    validate = DadosPessoais.objects.filter(usuario=request.user)
    paises = Paises.objects.all().order_by('name')
    estados = Estados.objects.filter(country=31).order_by('name')
    cidades = Cidades.objects.filter(country=31).order_by('name')
    
    if request.method == 'GET':
        form = DadosPessoaisForm(request.GET or None, user=request.user)

        if validate:
            form.fields['sexo'].initial         = DadosPessoais.objects.get(usuario=request.user).sexo
            form.fields['estado_civil'].initial = DadosPessoais.objects.get(usuario=request.user).estado_civil
        
    if request.method == 'POST':
        form = DadosPessoaisForm(request.POST or None, user=request.user)
        if form.is_valid():
            if validate:
                DadosPessoais.objects.filter(usuario=request.user).delete()
            form.save()
            messages.success(request, 'Cadastrado!')
            return redirect('perfil')
        else:
            messages.error(request, 'Não cadastrado! Por favor verifique se todos os campo os campos obrigatórios foram preenchidos e tente novamente.')
            return redirect('perfil')
        
    return render(request, "modals/cadastrar_dados_pessoais.html", {'form': form, 'validate': validate, 'paises': paises, 'estados': estados, 'cidades': cidades})


# Cadastro de Formacoes Academicas   
def FormacaoView(request):
    if not request.user.is_authenticated:
        return redirect("entrar")
    
    validate = Formacao.objects.filter(usuario=request.user)
    
    if request.method == 'GET':
        formset = FormacaoFormset(request.GET or None, prefix='formacoes')
        
    if request.method == 'POST':
        formset = FormacaoFormset(request.POST or None, prefix='formacoes')   
        if formset.is_valid():
            for form in formset:
                escolaridade = form.cleaned_data.get('escolaridade')
                instituicao = form.cleaned_data.get('instituicao')
                if form.cleaned_data.get('curso'):
                    curso = form.cleaned_data.get('curso')
                else:
                    curso = "Colegial"
                status_formacao = form.cleaned_data.get('status_formacao')
                if escolaridade and instituicao and curso and status_formacao:
                    Formacao(
                        escolaridade=escolaridade,
                        instituicao=instituicao,
                        curso=curso,
                        status_formacao=status_formacao,
                        usuario=request.user
                    ).save()
            messages.success(request, 'Cadastrado!')
            return redirect('perfil')
        else:
            messages.error(request, 'Não cadastrado! Por favor verifique se todos os campo os campos obrigatórios foram preenchidos e tente novamente.')
            return redirect('perfil')
        
    return render(request, "modals/cadastrar_formacoes_academicas.html", {'formset': formset, 'validate': validate})


# Exclusao de Formacoes Academicas 
def DeleteFormacaoView(request, nr_item):
    if not request.user.is_authenticated:
        return redirect("entrar")
   
    if request.method == 'GET':
        form = FormacaoForm(request.GET or None)

    elif request.method == 'POST':
        form = FormacaoForm(request.POST or None)

        cryptoid = int(nr_item, 16) - 3109786745873612405294780

        Formacao.objects.get(pk=cryptoid, usuario=request.user).delete()
        messages.success(request, 'Formação acadêmica removida com sucesso!')
        return redirect('perfil')

    return render(request, "modals/deletar_formacao_academica.html", {'form': form})


# Cadastro de Experiencias Profissionais    
def ExperienciaView(request):
    if not request.user.is_authenticated:
        return redirect("entrar")
    
    validate = Experiencia.objects.filter(usuario=request.user)
    
    if request.method == 'GET':
        formset = ExperienciaFormset(request.GET or None, prefix='experiencias')
        
    if request.method == 'POST':
        formset = ExperienciaFormset(request.POST or None, prefix='experiencias')      
        if formset.is_valid():
            for form in formset:
                empresa = form.cleaned_data.get('empresa')
                data_entrada = form.cleaned_data.get('data_entrada')
                if form.cleaned_data.get('data_saida'):
                    data_saida = form.cleaned_data.get('data_saida')
                else:
                    data_saida = "1900-01-01"
                atuacao = form.cleaned_data.get('atuacao')
                cargo_exp = form.cleaned_data.get('cargo_exp')
                atividades_exp = form.cleaned_data.get('atividades_exp')
                if empresa and data_entrada and data_saida and atuacao and cargo_exp and atividades_exp:
                    Experiencia(
                        empresa=empresa, 
                        data_entrada=data_entrada, 
                        data_saida=data_saida, 
                        atuacao=atuacao, 
                        cargo_exp=cargo_exp, 
                        atividades_exp=atividades_exp, 
                        usuario=request.user
                    ).save()
            messages.success(request, 'Cadastrado!')
            return redirect('perfil')
        else:
            messages.error(request, 'Não cadastrado! Por favor verifique se todos os campo os campos obrigatórios foram preenchidos e tente novamente.')
            return redirect('perfil')
        
    return render(request, "modals/cadastrar_experiencias_profissionais.html", {'formset': formset, 'validate': validate})


# Exclusao de Experiencias Profissionais  
def DeleteExperienciaView(request, nr_item):
    if not request.user.is_authenticated:
        return redirect("entrar")
   
    if request.method == 'GET':
        form = ExperienciaForm(request.GET or None)

    elif request.method == 'POST':
        form = ExperienciaForm(request.POST or None)

        cryptoid = int(nr_item, 16) - 3109786745873612405294780

        Experiencia.objects.get(pk=cryptoid, usuario=request.user).delete()
        messages.success(request, 'Experiência profissional removida com sucesso!')
        return redirect('perfil')

    return render(request, "modals/deletar_experiencia_profissional.html", {'form': form})


# Cadastro de Idiomas     
def IdiomaView(request):
    if not request.user.is_authenticated:
        return redirect("entrar")
    
    validate = Idioma.objects.filter(usuario=request.user)
    
    if request.method == 'GET':
        formset = IdiomaFormset(request.GET or None, prefix='idiomas')  
        
    if request.method == 'POST':
        formset = IdiomaFormset(request.POST or None, prefix='idiomas')   
        if formset.is_valid():
            for form in formset:
                idioma = form.cleaned_data.get('idioma')
                nivel_idioma = form.cleaned_data.get('nivel_idioma')
                if idioma and nivel_idioma:
                    Idioma(
                        idioma=idioma, 
                        nivel_idioma=nivel_idioma, 
                        usuario=request.user
                    ).save()
            messages.success(request, 'Cadastrado!')
            return redirect('perfil')
        else:
            messages.error(request, 'Não cadastrado! Por favor verifique se todos os campo os campos obrigatórios foram preenchidos e tente novamente.')
            return redirect('perfil')
        
    return render(request, "modals/cadastrar_idiomas.html", {'formset': formset, 'validate': validate})


# Exclusao de Idiomas     
def DeleteIdiomaView(request, nr_item):
    if not request.user.is_authenticated:
        return redirect("entrar")
   
    if request.method == 'GET':
        form = IdiomaForm(request.GET or None)

    elif request.method == 'POST':
        form = IdiomaForm(request.POST or None)

        cryptoid = int(nr_item, 16) - 3109786745873612405294780

        Idioma.objects.get(pk=cryptoid, usuario=request.user).delete()
        messages.success(request, 'Idioma removido com sucesso!')
        return redirect('perfil')

    return render(request, "modals/deletar_idioma.html", {'form': form})


# Cadastro de Conhecimentos Tecnológicos
def TecnologiaView(request):
    if not request.user.is_authenticated:
        return redirect("entrar")
    
    validate = Tecnologia.objects.filter(usuario=request.user)
    
    if request.method == 'GET':
        formset = TecnologiaFormset(request.GET or None, prefix='tecnologias')  
        
    if request.method == 'POST':
        formset = TecnologiaFormset(request.POST or None, prefix='tecnologias')   
        if formset.is_valid():
            for form in formset:
                sistema = form.cleaned_data.get('sistema')
                nivel_sistema = form.cleaned_data.get('nivel_sistema')
                if sistema and nivel_sistema:
                    Tecnologia(sistema=sistema, nivel_sistema=nivel_sistema, usuario=request.user).save()
            messages.success(request, 'Cadastrado!')
            return redirect('perfil')
        else:
            messages.error(request, 'Não cadastrado! Por favor verifique se todos os campo os campos obrigatórios foram preenchidos e tente novamente.')
            return redirect('perfil')
        
    return render(request, "modals/cadastrar_tecnologias.html", {'formset': formset, 'validate': validate})


# Exclusao de Conhecimentos Tecnológicos
def DeleteTecnologiaView(request, nr_item):
    if not request.user.is_authenticated:
        return redirect("entrar")
   
    if request.method == 'GET':
        form = TecnologiaForm(request.GET or None)

    elif request.method == 'POST':
        form = TecnologiaForm(request.POST or None)

        cryptoid = int(nr_item, 16) - 3109786745873612405294780

        Tecnologia.objects.get(pk=cryptoid, usuario=request.user).delete()
        messages.success(request, 'Tecnologia removida com sucesso!')
        return redirect('perfil')

    return render(request, "modals/deletar_tecnologia.html", {'form': form})


# Cadastro de Dados Complementares
def DadosComplementaresView(request):
    if not request.user.is_authenticated:
        return redirect("entrar")
    
    validate = Complementar.objects.filter(usuario=request.user)
    
    if request.method == 'GET':
        form = DadosComplementaresForm(request.GET or None, user=request.user)

        if validate:
            form.fields['interesse1'].initial = Complementar.objects.get(usuario=request.user).interesse1
            form.fields['interesse2'].initial = Complementar.objects.get(usuario=request.user).interesse2
            form.fields['inspecao'].initial   = Complementar.objects.get(usuario=request.user).inspecao
            form.fields['cnh'].initial        = Complementar.objects.get(usuario=request.user).cnh
            form.fields['distancia'].initial  = Complementar.objects.get(usuario=request.user).distancia
        
    if request.method == 'POST':
        form = DadosComplementaresForm(request.POST or None, user=request.user)        
        if form.is_valid():
            if validate:
                Complementar.objects.filter(usuario=request.user).delete()
            form.save()
            messages.success(request, 'Cadastrado!')
            return redirect('perfil')
        else:
            messages.error(request, 'Não cadastrado! Por favor verifique se todos os campo os campos obrigatórios foram preenchidos e tente novamente.')
            return redirect('perfil')
        
    return render(request, "modals/cadastrar_dados_complementares.html", {'form': form, 'validate': validate})


# HOME
def HomeView(request):
    return render(request, "main/home.html", {})


# Contatos
def ContatoView(request):
    if request.method == 'GET':
        form = ContatoForm()
    else:
        form = ContatoForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            from_email = form.cleaned_data['from_email']
            from_telefone = form.cleaned_data['from_telefone']
            message = form.cleaned_data['message']
            send_mail(subject, message + '\nContato: ' + from_telefone, from_email, ['suporte.recsel@coloradoagro.com.br'])
            messages.success(request, 'Dúvida enviada. Obrigado!', extra_tags='alert')
            return redirect("home")
        else:
            messages.error(request, 'Erro ao enviar sua dúvida. Por favor tente novamente!', extra_tags='alert')
            return redirect("home")
    return render(request, "main/contato.html", {'form': form})


# Ajuda
def AjudaView(request):
    if not request.user.is_authenticated:
        return redirect("entrar")
    
    return render(request, "main/perfil/ajuda.html", {})


# Cadastro de Questionario
def QuestionarioView(request):
    if not request.user.is_authenticated:
        return redirect("entrar")

    if Questionario.objects.filter(usuario=request.user):
        data_cadastro   = Questionario.objects.get(usuario=request.user).data_cadastro
        data_vencimento = data_cadastro.replace(year=(data_cadastro.year + 1)).strftime('%Y-%m-%d')
        data_atual      = datetime.datetime.now().strftime('%Y-%m-%d')

        if data_vencimento < data_atual:
            atualizar = True
            messages.warning(request, 'ATENÇÃO: Questionários só podem ser cadastrados uma vez ao ano. Preencha com anteção!')
        else:
            atualizar = False
            messages.warning(request, 'ATENÇÃO: Você já possui um questionário cadastrado. Prazo de permanência de 1 ano.')

    else:
        data_cadastro   = None
        atualizar       = True  
        messages.warning(request, 'ATENÇÃO: Questionários só podem ser cadastrados uma vez ao ano. Preencha com anteção!')

    if request.method == 'GET':
        form = QuestionarioForm(request.GET or None)
        
    if request.method == 'POST':
        if Questionario.objects.filter(usuario=request.user):
            Questionario.objects.filter(usuario=request.user).delete()

        Questionario(
            usuario=request.user,
            pergunta1=request.POST.get('pergunta1'),
            pergunta2=request.POST.get('pergunta2'),
            pergunta3=request.POST.get('pergunta3'),
            pergunta4=request.POST.get('pergunta4'),
            pergunta5=request.POST.get('pergunta5'),
            pontuacao_questionario=0,
            data_cadastro=datetime.datetime.now()
        ).save()

        messages.success(request, 'Questionário cadastrado com sucesso!', extra_tags='alert')
        return redirect("perfil")

    return render(request, 'modals/cadastrar_questionario.html', {
        'form': form, 
        'atualizar': atualizar, 
        'questionario': Questionario.objects.filter(usuario=request.user), 
        'data_cadastro': data_cadastro,
        })


# Cadastro de Documentos
def ArquivosView(request):
    if not request.user.is_authenticated:
        return redirect("entrar")
        
    validate = VagasUsuarios.objects.filter(usuario=request.user, status_cadastro=True, is_active=True)
    
    if request.method == 'GET':
        form = ArquivosForm(request.GET, request.FILES, user=request.user)
        
    if request.method == 'POST':
        form = ArquivosForm(request.POST, request.FILES, user=request.user)
        
        if not validate:
            messages.error(request, 'Você não pode enviar documentos ainda. Para enviar documentos você deve ter sido aprovado em algum processo seletivo.')
            return redirect('perfil')
    
        if form.is_valid():
            obj = form.save(commit=False)
            for f in request.FILES.getlist('documentos'):
                obj = Arquivos.objects.create(documentos=f, usuario=request.user)
            
            messages.success(request, 'Documentos salvos!', extra_tags='alert')
            return redirect('perfil')
        
        else:
            messages.error(request, 'Seus documentos não foram salvos. Por favor, tente novamente!')
            return redirect('perfil')

    return render(request, 'main/perfil/arquivos.html', {'form': form})


# Registrar Conta
def RegistrationView(request):
    context = {}
    if request.POST:
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            account = authenticate(email=email, password=raw_password)
            login(request, account)
            return redirect('perfil')
        else:
            context['registration_form'] = form
    else:
        form = RegistrationForm()
        context['registration_form'] = form
    return render(request, 'main/registrar.html', context)


# Logout Conta
def LogoutView(request):
    logout(request)
    return redirect('home')


# Login Conta
def LoginView(request):
    user = request.user
    if user.is_authenticated:
        return redirect('perfil')

    if request.POST:
        form = AccountAuthenticationForm(request.POST)
        if form.is_valid():
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(email=email, password=password)

            if user:
                login(request, user)
                if request.user.is_superuser:
                    return redirect('administracao')
                else:
                    return redirect('perfil')
                
    else:
        form = AccountAuthenticationForm()
        
    return render(request, 'main/entrar.html', {'login_form': form})


# Perfil
def ProfileView(request):
    if not request.user.is_authenticated:
        return redirect("entrar")    
    
    context = {
        'dados_pessoais': DadosPessoais.objects.filter(usuario=request.user),
        'formacoes': Formacao.objects.filter(usuario=request.user),
        'experiencias': Experiencia.objects.filter(usuario=request.user),
        'idiomas': Idioma.objects.filter(usuario=request.user),
        'tecnologias': Tecnologia.objects.filter(usuario=request.user),
        'dados_complementares': Complementar.objects.filter(usuario=request.user),
        'questionario': Questionario.objects.filter(usuario=request.user),
        'vagas': VagasUsuarios.objects.filter(usuario=request.user, is_active=True),
        'arquivos': VagasUsuarios.objects.filter(usuario=request.user, status_cadastro=True),
        'foto': ImagensPerfil.objects.filter(usuario=request.user).exclude(imagem__isnull=True).exclude(imagem__exact=''),
        'termo': Termo.objects.filter(usuario=request.user, status_termo=True)
    }

    count   = 0
    for i in context.values():
        if len(i) == 0:
            count += 1
    total = (len(context) - count) * 100 / (len(context) - 1)
    if total > 100:
        total = 100
    context['avanco'] = total
        
    if request.method == 'GET':
        form = ImagemForm(request.GET, request.FILES, user=request.user)
        context['form'] = form
        
    if request.method == 'POST':
        form = ImagemForm(request.POST, request.FILES, user=request.user)
        context['form'] = form
        
        if form.is_valid():
            if ImagensPerfil.objects.filter(usuario=request.user):
                ImagensPerfil.objects.filter(usuario=request.user).delete()
            form.save()            
            messages.success(request, 'Foto foi alterada com sucesso!', extra_tags='alert')
            return redirect('perfil')
        
        else:
            messages.error(request, 'Foto não foi alterada com sucesso. Por favor, tente novamente!')
            return redirect('perfil')

    return render(request, "main/perfil/perfil.html", context)
    

# Curriculo
def ResumeCurriculoView(request):
    if not request.user.is_authenticated:
        return redirect("entrar")

    context = {
        'dados_pessoais': DadosPessoais.objects.filter(usuario=request.user),
        'formacoes': Formacao.objects.filter(usuario=request.user),
        'experiencias': Experiencia.objects.filter(usuario=request.user),
        'idiomas': Idioma.objects.filter(usuario=request.user),
        'tecnologias': Tecnologia.objects.filter(usuario=request.user),
        'dados_complementares': Complementar.objects.filter(usuario=request.user),
    }

    return render(request, "main/perfil/curriculo.html", context)


# Vagas Cadastradas
def ResumeVagasView(request):
    if not request.user.is_authenticated:
        return redirect("entrar")

    minhas_vagas = VagasUsuarios.objects.filter(usuario=request.user, is_active=True).order_by('vaga__cargo__nome_cargo')

    return render(request, "main/perfil/vagas.html", {'minhas_vagas': minhas_vagas})


# Exclusao de Vagas Cadastradas
def DeleteVagaView(request, nr_item):
    cryptoid = int(nr_item, 16) - 3109786745873612405294780

    if not request.user.is_authenticated:
        return redirect("entrar")
   
    if request.method == 'GET':
        form = VagasUsuariosForm(request.GET or None)

    elif request.method == 'POST':
        form = VagasUsuariosForm(request.POST or None)
        VagasUsuarios.objects.filter(pk=cryptoid, usuario=request.user).update(is_active=False)
        messages.success(request, 'Vaga removida com sucesso!', extra_tags='alert')
        return redirect('perfil')

    return render(request, "main/perfil/deletar_vaga.html", {'form': form})

 
# Vagas Abertas
def VagasView(request):
    validate = Vagas.objects.filter(Q(status_vaga=True)).order_by('data_validade')

    query = request.GET.get('q')
    if query:
        validate = Vagas.objects.filter(regiao__nome__icontains=query)

    return render(request, "main/vagas.html", {'validate': validate})


# Cadastro de Vagas
def DetalhesVagaView(request, nr_item):
    cryptoid = int(nr_item, 16) - 3109786745873612405294780
    item = get_object_or_404(Vagas, pk=cryptoid)
    validate = Vagas.objects.filter(pk=cryptoid)
    
    if request.method == 'GET':
        form = VagasUsuariosFormset(request.GET or None, prefix='cadvaga')

    if request.method == 'POST':

        if not request.user.is_authenticated:
            return redirect("entrar")

        if not DadosPessoais.objects.filter(usuario=request.user) or not Complementar.objects.filter(usuario=request.user) or not Formacao.objects.filter(usuario=request.user):
            messages.error(request, 'Para se candidatar à uma vaga, certifique-se de ter cadastrado seus Dados Pessoais, Formações Acadêmicas e Dados Complementares primeiro!')
            return redirect("vagas")

        if VagasUsuarios.objects.filter(usuario=request.user, is_active=True).count() > 0:
            messages.error(request, 'Você só pode se cadastrar em uma Vaga por vez. Para se candidatar em uma nova vaga, entre em seu perfil e exclua a vaga já cadastrada!', extra_tags='alert')
            return redirect("vagas")
            
        try:
            VagasUsuarios.objects.get(usuario=request.user, vaga=item, is_active=True)
            messages.error(request, 'Vaga já cadastrada. Selecione outra!', extra_tags='alert')
            return redirect("vagas")

        except:
            VagasUsuarios(
                vaga=item,  
                status_cadastro=False,
                pontuacao_vaga=0,
                usuario=request.user,
                is_active=True
                ).save()
            messages.success(request, 'Vaga cadastrada com sucesso!', extra_tags='alert')
            return redirect("vagas")

    return render(request, "main/detalhes_vaga.html", {
        'form': form,
        'validate': validate,
    })
    
       
# Termos de Uso
def TermoView(request):
    if not request.user.is_authenticated:
        return redirect("entrar")
    
    validate = Termo.objects.filter(usuario=request.user, status_termo=1)
    
    if request.method == 'GET':
        form = TermoForm(request.GET or None, user=request.user)  
        
    if request.method == 'POST':
        form = TermoForm(request.POST or None, user=request.user)   
        if form.is_valid():
            Termo(
                data_termo=datetime.datetime.now(), 
                status_termo=form.cleaned_data['status_termo'], 
                usuario=request.user
            ).save()
            return redirect('perfil')
        else:
            messages.error(request, 'Não cadastrado! Por favor verifique se todos os campo os campos obrigatórios foram preenchidos e tente novamente.')
            return redirect('perfil')
        
    return render(request, "main/termo.html", {'form': form, 'validate': validate})


# Cookies
def CookiesView(request):
    context = {}
    return render(request, "main/cookies.html", context)


# Entrar em: Lib\site-packages\django\contrib\auth\views.py

# Adicionar as libs abaixo:
    # from django.contrib import messages
    # from django.shortcuts import redirect


# Na classe PasswordChangeView alterar a linha:         
    # success_url = reverse_lazy("perfil")
# Dentro de PasswordChangeView alterar função form_valid para:
    # def form_valid(self, form):
    #         form.save()
    #         messages.success(self.request, 'Senha alterada com sucesso!')
    #         return redirect("home")


# Na classe PasswordResetView alterar a linha:          
    # success_url = reverse_lazy("home")
# Dentro de PasswordResetView adicionar as linhas abaixo após form.save(**opts):
    # messages.success(self.request, 'Dados eviados. Por favor verifique seu email para alterar sua senha!')
    # return redirect("home")
        

# Na classe PasswordResetConfirmView alterar linha:     
    # success_url = reverse_lazy("entrar")
# Dentro de PasswordResetConfirmView na função dispatch alterar ultimas linhas para:
    # messages.error(self.request, 'Este link já foi utilizado ou expirou o tempo para alteração da senha. Por favor reenvie a solicitação ao seu email, ou entre em contato com o suporte.')
    # return redirect('password_reset')
# Dentro de PasswordResetConfirmView na função form_valid alterar ultimas linhas para:
    # messages.success(self.request, 'Senha alterada com sucesso!')
    # return redirect("home")