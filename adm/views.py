from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import render_to_string, get_template
from django.shortcuts import render, redirect
from django.core.mail import EmailMultiAlternatives
from email.mime.image import MIMEImage
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from xhtml2pdf import pisa
from datetime import datetime, timedelta
from io import BytesIO

from main.models import (
    Cidades, Filial, Contas, Cargos, Setores, DadosPessoais, Formacao, Experiencia, Idioma, Tecnologia, Complementar,
    Vagas, VagasUsuarios, Questionario, Arquivos, ImagensPerfil, Fase, FaseUsuario, Requisicao,
    PRIORIDADE, CONTRATOS, SEXO, ESCOLARIDADE, EXTINT
)

from adm.forms import (CadReqForm, CadVagaForm, CadCargoForm, CadSetorForm, CadFaseForm, CadUserFaseForm)

import os


base_dir        = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
contratos       = [i[1] for i in CONTRATOS]
prioridades     = [i[1] for i in PRIORIDADE]
generos         = [i[1] for i in SEXO]
escolaridade    = [i[1] for i in ESCOLARIDADE]
exitint         = [i[1] for i in EXTINT]


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    return HttpResponse(result.getvalue(), content_type='application/pdf')
    

def logo_data():
    assinatura = os.path.join(base_dir, 'static/assinatura/cmaquinas.jpg')
    with open(assinatura, 'rb') as f:
        logo_data = f.read()
    logo = MIMEImage(logo_data)
    logo.add_header('Content-ID', '<logo>')
    return logo


def enviar_email_aprovacao(nr_item):
    user = Contas.objects.get(id=nr_item)
    assunto = 'Aprovação Processo Seletivo - Colorado Máquinas John Deere'
    remetente = 'trabalheconosco@coloradoagro.com.br'
    destinatario = user.email
    mensagem = render_to_string('mails/send_email_aprovacao.html')
    message = EmailMultiAlternatives(assunto, mensagem, remetente, [destinatario])
    ctps1 = os.path.join(base_dir, 'documentos/ctps_digital_01.jpeg')
    ctps2 = os.path.join(base_dir, 'documentos/ctps_digital_02.jpeg')
    esocial = os.path.join(base_dir, 'documentos/questionario_esocial.docx')
    doc = os.path.join(base_dir, 'documentos/relacao_documentos.xlsx')
    message.attach_file(ctps1)
    message.attach_file(ctps2)
    message.attach_file(esocial)
    message.attach_file(doc)
    message.attach(logo_data())
    message.send()


def enviar_email_reprovacao(nr_item):
    user = Contas.objects.get(id=nr_item)
    assunto = 'Devolutiva Processo Seletivo - Colorado Máquinas John Deere'
    remetente = 'trabalheconosco@coloradoagro.com.br'
    destinatario = user.email
    mensagem = render_to_string('mails/send_email_reprovacao.html')
    message = EmailMultiAlternatives(assunto, mensagem, remetente, [destinatario])
    message.attach(logo_data())
    message.send()


def AdministracaoView(request):
    if not request.user.is_authenticated:
        return redirect('entrar')

    if not request.user.is_admin:
        return redirect('perfil')
    
    data = dict()
    for i in range(2020, 2023):
        data[i] = Contas.objects.all().filter(data_inscricao__year=i).count()

    vagas   = Vagas.objects.all().order_by('-status_vaga')
    vaga_page = request.GET.get('vaga-page', 1)
    paginator = Paginator(vagas, 10)
    try:
        vagas = paginator.page(vaga_page)
    except PageNotAnInteger:
        vagas = paginator.page(1)
    except EmptyPage:
        vagas = paginator.page(paginator.num_pages)
    
    setores = Setores.objects.all().order_by('id')
    page = request.GET.get('setores-page', 1)
    paginator = Paginator(setores, 10)
    try:
        setores = paginator.page(page)
    except PageNotAnInteger:
        setores = paginator.page(1)
    except EmptyPage:
        setores = paginator.page(paginator.num_pages)

    cargos  = Cargos.objects.all().order_by('id')
    page = request.GET.get('cargos-page', 1)
    paginator = Paginator(cargos, 10)
    try:
        cargos = paginator.page(page)
    except PageNotAnInteger:
        cargos = paginator.page(1)
    except EmptyPage:
        cargos = paginator.page(paginator.num_pages)

    fases   = Fase.objects.all().order_by('id')
    page = request.GET.get('fases-page', 1)
    paginator = Paginator(fases, 10)
    try:
        fases = paginator.page(page)
    except PageNotAnInteger:
        fases = paginator.page(1)
    except EmptyPage:
        fases = paginator.page(paginator.num_pages)

    return render(request, 'administracao.html', {
        'vagas': vagas,
        'setores': setores,
        'cargos': cargos,
        'data': data,
        'fases': fases,
    })

#########################--CADASTROS--#########################
# CADASTRO DE REQUISIÇÃO
def CadReqAdmin(request):
    if not request.user.is_authenticated:
        return redirect('entrar')
    
    if request.method == 'GET':
        form = CadReqForm(request.GET or None)

    if request.method == 'POST':
        new_request = request.POST.copy()
        new_request.update({
            'status_a': True,
            'usuario_a': request.user.id,
            'data_a': datetime.now()
        })
        form = CadReqForm(new_request)
        if form.is_valid():
            form.save()
            messages.success(request, 'Requisição cadastrada!')

            destinatario    = "rh@coloradoagro.com.br"
            assunto         = "Requisição (Nível 1) - Trabalhe Conosco"
            remetente       = "trabalheconosco@coloradoagro.com.br"
            mensagem        = "Uma nova requisição foi cadastrada. Por favor, entre no sistema para verificação."
            message         = EmailMultiAlternatives(assunto, mensagem, remetente, [destinatario])
            message.send()

            return redirect('requisicoes')
        else:
            messages.error(request, 'Ops, algo deu errado. Por favor, tente novamente!')
            return redirect('cadastrar_requisicao')

    return render(request, 'cadastrar/cadastrar_requisicao.html', {'form': form})


# APROVACOES DE REQUISIÇÕES
def AprovaAdmin(request):
    if not request.user.is_authenticated:
        return redirect('entrar')
    
    context = {}
    requisicoes = Requisicao.objects.all().filter(is_active=True).order_by('-data_a')

    if request.user.is_rh and request.user.is_gestor:
        context['requisicoes'] = requisicoes.filter(status_a=True,status_c=False,status_d=False)
    elif request.user.is_rh:
        context['requisicoes'] = requisicoes.filter(status_a=True,status_b=False,status_c=False,status_d=False)
    elif request.user.is_gestor:
        context['requisicoes'] = requisicoes.filter(status_a=True,status_b=True,status_c=False,status_d=False,gestor=request.user)
    elif request.user.is_diretor:
        context['requisicoes'] = requisicoes.filter(status_a=True,status_b=True,status_c=True,status_d=False)
    else:
        context['requisicoes'] = None

    if request.method == 'POST':
        if request.POST.get('recusa_total') is not None:
            Requisicao.objects.filter(pk=request.POST.get('recusa_total')).update(
                status_b=False,
                status_c=False,
                status_d=False,
            )

            uid             = Requisicao.objects.get(pk=request.POST.get('recusa_total')).usuario_a
            req             = Requisicao.objects.get(pk=request.POST.get('recusa_total')).codigo
            destinatario    = uid.email
            assunto         = "Requisição (Nível 1) - Trabalhe Conosco"
            remetente       = "trabalheconosco@coloradoagro.com.br"
            mensagem        = "A requisição código: " + str(req) + " foi recusada. Por favor, entre no sistema para verificação."
            message         = EmailMultiAlternatives(assunto, mensagem, remetente, [destinatario])
            message.send()

            messages.success(request, 'Recusado!', extra_tags='alert')   
            return redirect('aprovacoes')

        if request.POST.get('aprovar_nivel_a') is not None:
            Requisicao.objects.filter(pk=request.POST.get('aprovar_nivel_a')).update(
                status_b=True,
                data_b=datetime.now(),
                usuario_b=request.user
            )

            uid             = Requisicao.objects.get(pk=request.POST.get('aprovar_nivel_a')).gestor
            req             = Requisicao.objects.get(pk=request.POST.get('aprovar_nivel_a')).codigo
            destinatario    = uid.email
            assunto         = "Requisição (Nível 2) - Trabalhe Conosco"
            remetente       = "trabalheconosco@coloradoagro.com.br"
            mensagem        = "Uma nova requisição está esperando por sua aprovação. Por favor, entre no sistema para verificação."
            message         = EmailMultiAlternatives(assunto, mensagem, remetente, [destinatario])
            message.send()

            messages.success(request, 'Aprovado!', extra_tags='alert')   
            return redirect('aprovacoes')
        
        if request.POST.get('aprovar_nivel_b') is not None:
            Requisicao.objects.filter(pk=request.POST.get('aprovar_nivel_b')).update(
                status_c=True,
                data_c=datetime.now(),
                usuario_c=request.user
            )

            assunto         = "Requisição (Nível 3) - Trabalhe Conosco"
            remetente       = "trabalheconosco@coloradoagro.com.br"
            mensagem        = "Uma nova requisição está esperando por sua aprovação. Por favor, entre no sistema para verificação."
            message         = EmailMultiAlternatives(assunto, mensagem, remetente, ['marcio.piola@coloradoagro.com.br', 'joao.falaschi@coloradoagro.com.br'])
            message.send()

            messages.success(request, 'Aprovado!', extra_tags='alert')   
            return redirect('aprovacoes')
        
        if request.POST.get('aprovar_nivel_c') is not None:
            Requisicao.objects.filter(pk=request.POST.get('aprovar_nivel_c')).update(
                status_d=True,
                data_d=datetime.now(),
                usuario_d=request.user
            )

            req = Requisicao.objects.get(pk=request.POST.get('aprovar_nivel_c'))
            cod = Vagas.objects.all().last().codigo_vaga

            Vagas(
                codigo_vaga=(int(cod) + 1),
                status_vaga=True,
                prioridade="Média",
                data_validade=(datetime.now() + timedelta(30)),
                quantidade=1,
                jornada="07:30 às 17:30",
                ensino=req.ensino,
                contratacao=req.tipo_vaga,
                regiao=req.filial,
                atividades=req.atividades,
                qualificacao=req.habilidades,
                descricao=req.informacoes,
                cargo=req.cargo,
                setor=req.setor
            ).save()
            messages.success(request, 'Aprovado!', extra_tags='alert')   
            return redirect('aprovacoes')

    return render(request, 'aprovacoes.html', context)


# CADASTRO DE FASES
def CadFaseAdmin(request):
    if not request.user.is_authenticated:
        return redirect('entrar')
    
    if not request.user.is_admin:
        return redirect('perfil')
    
    if request.method == 'GET':
        form = CadFaseForm(request.GET or None)
        
    if request.method == 'POST':
        form = CadFaseForm(request.POST or None)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fase cadastrada!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            messages.error(request, 'Ops, algo deu errado. Por favor, tente novamente!')
            return redirect('cadastrar_fases')
        
    return render(request, 'cadastrar/cadastrar_fases.html', {'form':form})


# CADASTRO DE FASES_USUARIOS
def CadFaseUsuarioAdmin(request, nr_item):    
    if not request.user.is_authenticated:
        return redirect('entrar')
    
    if not request.user.is_admin:
        return redirect('perfil')
   
    userx = VagasUsuarios.objects.filter(pk=nr_item)
    if request.method == 'POST':
        a = request.POST.get('id_vaga_usuario')
        b = request.POST.get('fase')
        c = request.POST.get('observacao')
        if a is not None and b is not None:
            if a != '' and b != '':
                user = VagasUsuarios.objects.get(pk=a) 
                fase = Fase.objects.get(fase=b)
                FaseUsuario(usuario=user.usuario, fase=fase, observacao=c, vaga=user.vaga).save()
                messages.success(request, 'Fase cadastrada!')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
    return render(request, 'cadastrar/cadastrar_faseusuario.html', {'userx':userx})


# CADASTRO DE VAGAS
def CadVagaAdmin(request):
    if not request.user.is_authenticated:
        return redirect('entrar')
    
    if not request.user.is_admin:
        return redirect('perfil')
    
    if request.method == 'GET':
        form = CadVagaForm(request.GET or None)
        
    if request.method == 'POST':
        #new_request = request.POST.copy()
        #new_request.update({
        #    'setor': Setores.objects.get(pk=request.POST.get('setor')),
        #    'cargo': Cargos.objects.get(pk=request.POST.get('cargo')),
        #    'regiao': Filial.objects.get(pk=request.POST.get('regiao')),
        #})
        #form = CadVagaForm(new_request)
        form = CadVagaForm(request.POST or None)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vaga cadastrada!')
            return redirect('cadastrar_vagas')
        else:
            messages.error(request, 'Ops, algo deu errado. Por favor, tente novamente!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
    return render(request, 'cadastrar/cadastrar_vagas.html', {'form':form})


# CADASTRO DE CARGOS
def CadCargoAdmin(request):
    if not request.user.is_authenticated:
        return redirect('entrar')
    
    if not request.user.is_admin:
        return redirect('perfil')
    
    if request.method == 'GET':
        form = CadCargoForm(request.GET or None)
        
    if request.method == 'POST':
        form = CadCargoForm(request.POST or None)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cargo cadastrado!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            messages.error(request, 'Ops, algo deu errado. Por favor, tente novamente!')
            return redirect('cadastrar_cargos')
        
    return render(request, 'cadastrar/cadastrar_cargos.html', {'form':form})


# CADASTRO DE SETORES 
def CadSetorAdmin(request):
    if not request.user.is_authenticated:
        return redirect('entrar')
    
    if not request.user.is_admin:
        return redirect('perfil')
    
    if request.method == 'GET':
        form = CadSetorForm(request.GET or None)
        
    if request.method == 'POST':
        form = CadSetorForm(request.POST or None)
        if form.is_valid():
            form.save()
            messages.success(request, 'Setor cadastrado!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            messages.error(request, 'Ops, algo deu errado. Por favor, tente novamente!')
            return redirect('cadastrar_setores')
        
    return render(request, 'cadastrar/cadastrar_setores.html', {'form':form})

#########################--VISUALIZAÇÃO--#########################
# VISUALIZAÇÃO DE REQUISIÇÕES
def RequisicaoAdmin(request):
    if not request.user.is_authenticated:
        return redirect('entrar')
    
    if not request.user.is_admin:
        return redirect('perfil')
    
    if request.user.is_diretor or request.user.is_rh:
        requisicoes = Requisicao.objects.all().filter(is_active=True).order_by('-data_a')
    elif request.user.is_gestor:
        requisicoes = Requisicao.objects.all().filter(is_active=True,gestor=request.user).order_by('-data_a')
    else:    
        requisicoes = Requisicao.objects.all().filter(is_active=True, usuario_a=request.user).order_by('-data_a')

    query = request.GET.get('q')
    if query:
        requisicoes = requisicoes.filter(codigo=query)

    return render(request, 'requisicoes.html', {'requisicoes':requisicoes})

# VISUALIZAÇÃO DE CURRÍCULO
def CurriculoAdmin(request, nr_item):
    if not request.user.is_authenticated:
        return redirect('entrar')
    
    if not request.user.is_admin:
        return redirect('perfil')
    
    pdfuser = Contas.objects.get(id=nr_item)
    data = {
        'itensDadosPessoais': DadosPessoais.objects.filter(usuario=pdfuser),
        'itensFormacao': Formacao.objects.filter(usuario=pdfuser),
        'itensIdioma': Idioma.objects.filter(usuario=pdfuser),
        'itensExperiencia': Experiencia.objects.filter(usuario=pdfuser),
        'itensTecnologia': Tecnologia.objects.filter(usuario=pdfuser),
        'itensComplementar': Complementar.objects.filter(usuario=pdfuser),
        'itensQuestionario': Questionario.objects.filter(usuario=pdfuser),
        'itensFases': FaseUsuario.objects.filter(usuario=pdfuser),
        'itensVagasUsuario': VagasUsuarios.objects.filter(usuario=pdfuser),
    }
    pdf = render_to_pdf('invoice.html', data)
    return HttpResponse(pdf, content_type='application/pdf')


# VISUALIZAÇÃO DE CONTAS
def ContasAdmin(request):
    if not request.user.is_authenticated:
        return redirect('entrar')
    
    if not request.user.is_admin:
        return redirect('perfil')
    
    usuarios = Contas.objects.all().order_by('-data_inscricao')

    query = request.GET.get('q')
    bloqueados = request.GET.get('s')
    
    if query:
        usuarios = usuarios.filter(username__icontains=query)
    if bloqueados == 'Bloqueados':
        usuarios = usuarios.filter(is_active=False)
    elif bloqueados == 'Ativos':
         usuarios = usuarios.filter(is_active=True)
    
    if request.method == 'POST':
        if request.POST.get('remove_ativo') is not None and request.POST.get('remove_ativo') != '': 
            Contas.objects.filter(pk=request.POST.get('remove_ativo')).update(is_active=False)

        if request.POST.get('add_ativo') is not None and request.POST.get('add_ativo') != '': 
            Contas.objects.filter(pk=request.POST.get('add_ativo')).update(is_active=False)        

        if request.POST.get('remove_interno') is not None and request.POST.get('remove_interno') != '': 
            Contas.objects.filter(pk=request.POST.get('remove_interno')).update(is_interno=False)

        if request.POST.get('add_interno') is not None and request.POST.get('add_interno') != '': 
            Contas.objects.filter(pk=request.POST.get('add_interno')).update(is_interno=True)

        if request.POST.get('remove_gestor') is not None and request.POST.get('remove_gestor') != '': 
            Contas.objects.filter(pk=request.POST.get('remove_gestor')).update(is_gestor=False)

        if request.POST.get('add_gestor') is not None and request.POST.get('add_gestor') != '': 
            Contas.objects.filter(pk=request.POST.get('add_gestor')).update(is_gestor=True)

        if request.POST.get('remove_admin') is not None and request.POST.get('remove_admin') != '': 
            Contas.objects.filter(pk=request.POST.get('remove_admin')).update(is_admin=False)

        if request.POST.get('add_admin') is not None and request.POST.get('add_admin') != '': 
            Contas.objects.filter(pk=request.POST.get('add_admin')).update(is_admin=True)

        return redirect('contas')

    page = request.GET.get('page', 1)
    paginator = Paginator(usuarios, 200)
    try:
        usuarios = paginator.page(page)
    except PageNotAnInteger:
        usuarios = paginator.page(1)
    except EmptyPage:
        usuarios = paginator.page(paginator.num_pages)
    
    return render(request, 'contas.html', {'usuarios':usuarios})


# VISUALIZAÇÃO DE CURRICULOS
def CurriculosAdmin(request):
    if not request.user.is_authenticated:
        return redirect('entrar')
    
    if not request.user.is_admin:
        return redirect('perfil')
    
    curriculos      = DadosPessoais.objects.all().order_by('id')
    username        = request.GET.get('q')
    regiao          = request.GET.get('p')
    interesse       = request.GET.get('r')
    escola          = request.GET.get('c')
    experiencia     = request.GET.get('n')
    data_inicial    = request.GET.get('s')
    data_final      = request.GET.get('t')

    if username:
        curriculos = curriculos.filter(usuario__username__icontains=username)
    if regiao:
        curriculos = curriculos.filter(cidade__name=regiao)
    if interesse:
        users = Complementar.objects.filter(interesse1__nome_setor=interesse).values_list('usuario', flat=True)
        curriculos = curriculos.filter(usuario__in=users)
    if escola:
        userx = Formacao.objects.filter(escolaridade=escola).values_list('usuario', flat=True)
        curriculos = curriculos.filter(usuario__in=userx)
    if experiencia:
        userw = Experiencia.objects.filter(atividades_exp__icontains=experiencia).values_list('usuario', flat=True)
        curriculos = curriculos.filter(usuario__in=userw)
    if data_final and data_final:
        curriculos = curriculos.filter(data_cadastro__range=[data_inicial, data_final])

    context = {
        'curriculos': curriculos,
        'regiao': Cidades.objects.all().filter(country_id=31).order_by('name'), 
        'interesses': Setores.objects.all().order_by('nome_setor'), 
        'escolaridade': escolaridade
    }    
    
    page = request.GET.get('curriculos-page', 1)
    paginator = Paginator(curriculos, 10)
    try:
        curriculos = paginator.page(page)
    except PageNotAnInteger:
        curriculos = paginator.page(1)
    except EmptyPage:
        curriculos = paginator.page(paginator.num_pages)
    
    return render(request, 'curriculos.html', context)
    

# VISUALIZAÇÃO DE DOCUMENTOS
def DocumentosAdmin(request):
    if not request.user.is_authenticated:
        return redirect('entrar')
    
    if not request.user.is_admin:
        return redirect('perfil')
    
    documentos = Arquivos.objects.all().order_by('-data_envio')

    query = request.GET.get('q')    
    if query:
        documentos = documentos.filter(documentos__icontains=query)
    
    return render(request, 'documentos.html', {'documentos':documentos})
    

# VISUALIZAÇÃO DE QUESTIONÁRIOS
def QuestionariosAdmin(request):
    if not request.user.is_authenticated:
        return redirect('entrar')
    
    if not request.user.is_admin:
        return redirect('perfil')
    
    questionarios = Questionario.objects.all().order_by('-data_cadastro')

    query = request.GET.get('q')
    if query:
        questionarios = questionarios.filter(usuario__username__icontains=query)
    
    return render(request, 'questionarios.html', {'questionarios':questionarios}) 


# VISUALIZAÇÃO DE FASES
def FasesAdmin(request):
    if not request.user.is_authenticated:
        return redirect('entrar')
    
    if not request.user.is_admin:
        return redirect('perfil')
    
    fases = FaseUsuario.objects.all().order_by('usuario')
    fasenames = Fase.objects.all()
    vagas = Vagas.objects.all().filter(status_vaga=True)
    
    usuario = request.GET.get('q')
    vaga = request.GET.get('p')
    fase = request.GET.get('r')
    data_min = request.GET.get('s')
    data_max = request.GET.get('t')
    
    if usuario is not None and usuario != '':
        fases = fases.filter(usuario__username__icontains=usuario)
    if vaga is not None and vaga != '':
        if "|" not in vaga[:3]:
            codvaga = vaga[:3]
        else:
            codvaga = vaga[:2]
        objvaga = Vagas.objects.get(codigo_vaga=codvaga)
        fases = fases.filter(vaga=objvaga.id)
    if fase is not None and fase != '':
        objfase = Fase.objects.get(fase=fase)
        fases = fases.filter(fase = objfase.id)
    if data_min is not None and data_min != '' and data_max is not None and data_max != '':
        fases = fases.filter(data_cadastro__range = (data_min, data_max))
        
    if request.method == 'POST':
        notificacao = request.POST.get('notificacao_id')
        if notificacao is not None:
            fase_usuario = FaseUsuario.objects.get(pk=notificacao)
            wpp = DadosPessoais.objects.get(usuario=fase_usuario.usuario).celular.replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
            texto = Fase.objects.get(fase=fase_usuario.fase).descricao_fase
            httpwpp = "https://api.whatsapp.com/send?phone=55" + str(wpp) + "&text=" + texto
            return redirect(httpwpp)
            
        
        a = request.POST.get('id_userfase')
        b = request.POST.get('fase')
        c = request.POST.get('observacao')
        d = request.POST.get('id_vagafase')
        if a is not None and b is not None:
            if a != '' and b != '':
                user = Contas.objects.get(pk=a) 
                fase = Fase.objects.get(fase=b)
                vaga = Vagas.objects.get(pk=d)
                FaseUsuario(usuario=user, fase=fase, observacao=c, vaga=vaga).save()
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
    return render(request, 'fases.html', {'fases':fases, 'vagas':vagas, 'fasenames':fasenames}) 

#########################--EXCLUSÃO--#########################
# EXCLUSÃO DE VAGAS
def DelVagaAdmin(request, nr_item):
    if not request.user.is_authenticated:
        return redirect('entrar')

    if not request.user.is_admin:
        return redirect('perfil')
   
    if request.method == 'GET':
        form = CadVagaForm(request.GET or None)

    elif request.method == 'POST':
        form = CadVagaForm(request.POST or None)

        Vagas.objects.get(pk=nr_item).delete()
        messages.success(request, 'Vaga excluida!')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return render(request, 'deletar/deletar_vaga.html', {'form': form})


# EXCLUSÃO DE SETORES
def DelSetorAdmin(request, nr_item):
    if not request.user.is_authenticated:
        return redirect('entrar')
    
    if not request.user.is_admin:
        return redirect('perfil')
   
    if request.method == 'GET':
        form = CadSetorForm(request.GET or None)

    elif request.method == 'POST':
        form = CadSetorForm(request.POST or None)

        Setores.objects.get(pk=nr_item).delete()
        messages.success(request, 'Setor excluido!')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return render(request, 'deletar/deletar_setor.html', {'form': form})


# EXCLUSÃO DE CARGOS
def DelCargoAdmin(request, nr_item):
    if not request.user.is_authenticated:
        return redirect('entrar')
    
    if not request.user.is_admin:
        return redirect('perfil')
   
    if request.method == 'GET':
        form = CadCargoForm(request.GET or None)

    elif request.method == 'POST':
        form = CadCargoForm(request.POST or None)

        Cargos.objects.get(pk=nr_item).delete()
        messages.success(request, 'Cargo excluido!')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return render(request, 'deletar/deletar_cargo.html', {'form': form})


# EXCLUSÃO DE CARGOS
def DelFaseAdmin(request, nr_item):
    if not request.user.is_authenticated:
        return redirect('entrar')
    
    if not request.user.is_admin:
        return redirect('perfil')
   
    if request.method == 'GET':
        form = CadFaseForm(request.GET or None)

    elif request.method == 'POST':
        form = CadFaseForm(request.POST or None)

        Fase.objects.get(pk=nr_item).delete()
        messages.success(request, 'Fase excluida!')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return render(request, 'deletar/deletar_cargo.html', {'form': form})


# EXCLUSÃO DE FASES DO USUARIO
def DelFaseUsuarioAdmin(request, nr_item):
    if not request.user.is_authenticated:
        return redirect('entrar')
    
    if not request.user.is_admin:
        return redirect('perfil')
    
    faseuser = FaseUsuario.objects.get(pk=nr_item)
   
    if request.method == 'POST':
        FaseUsuario.objects.get(pk=nr_item).delete()
        return redirect('fases')

    return render(request, 'deletar/deletar_fase_usuario.html', {'faseuser': faseuser})


#########################--ALTERAÇÃO--#########################
# ALTERAÇÃO DA REQUISIÇÃO
def UpdateReqAdmin(request, nr_item):
    if not request.user.is_authenticated:
        return redirect('entrar')
    
    if not request.user.is_admin:
        return redirect('perfil')
    
    context = {
        'requisicao': Requisicao.objects.filter(pk=nr_item),
        'filiais': Filial.objects.all().order_by('cidade'),
        'gestores': Contas.objects.all().filter(is_gestor=True).order_by('username'),
        'setores': Setores.objects.all().order_by('nome_setor'),
        'cargos': Cargos.objects.all().order_by('nome_cargo'),
        'contratos': contratos, 
        'escolaridade': escolaridade,
        'exitint': exitint
    }

    if request.method == 'POST':
        if request.POST.get('alterar_requisicao') is not None:
            Requisicao.objects.filter(pk=nr_item).update(
                codigo=request.POST.get('codigo'),	
                salario=request.POST.get('salario'),		
                gestor=request.POST.get('gestor'),	
                tipo=request.POST.get('tipo'),	
                requisitos=request.POST.get('requisitos'),	
                atividades=request.POST.get('atividades'),	
                habilidades=request.POST.get('habilidades'),	
                ferramentas=request.POST.get('ferramentas'),	
                recrutamento=request.POST.get('recrutamento'),	
                informacoes=request.POST.get('informacoes'),	
                cargo=request.POST.get('cargo'),	
                filial=request.POST.get('filial'),	
                setor=request.POST.get('setor'),	
                tipo_vaga=request.POST.get('tipo_vaga'),	
                ensino=request.POST.get('ensino')
            )
        if request.POST.get('excluir_requisicao') is not None:
            Requisicao.objects.filter(pk=nr_item).update(is_active=False)
            messages.success(request, 'Requisição removida!')
            return redirect('requisicoes')
        
        messages.success(request, 'Requisição alterada!')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return render(request, 'update/update_requisicao.html', context)

# ALTERAÇÃO DO STATUS DA VAGA
def UpdateVagaAdmin(request, nr_item):
    if not request.user.is_authenticated:
        return redirect('entrar')
    
    if not request.user.is_admin:
        return redirect('perfil')
    
    vaga = Vagas.objects.filter(pk=nr_item)
    cargos = Cargos.objects.all().order_by('nome_cargo')
    setores = Setores.objects.all().order_by('nome_setor')
    filiais = Filial.objects.all().order_by('cidade')
    
    if request.method == 'POST':
        if request.POST.get('status_vaga') is None:
                status = False
        else: 
            status = True
        Vagas.objects.filter(pk=nr_item).update(
            codigo_vaga=request.POST.get('codigo_vaga'),
            status_vaga=status,
            prioridade=request.POST.get('prioridade'),
            data_validade=request.POST.get('data_validade'),
            quantidade=request.POST.get('quantidade'),
            jornada=request.POST.get('jornada'),
            ensino=request.POST.get('ensino'),
            contratacao=request.POST.get('contratacao'),
            regiao=request.POST.get('regiao'),
            atividades=request.POST.get('atividades'),
            qualificacao=request.POST.get('qualificacao'),
            descricao=request.POST.get('descricao'),
            cargo=Cargos.objects.get(pk=request.POST.get('cargo')),
            setor=Cargos.objects.get(pk=request.POST.get('setor'))
        )
        messages.success(request, 'Vaga alterada!')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return render(request, 'update/update_vaga.html', {'vaga': vaga, 'cargos': cargos, 'setores': setores, 'filiais': filiais,
    'contratos': contratos, 'prioridades': prioridades, 'escolaridade': escolaridade})


# ALTERAÇÃO DO STATUS DA VAGA
def UpdateStatVagaAdmin(request, nr_item):
    if not request.user.is_authenticated:
        return redirect('entrar')
    
    if not request.user.is_admin:
        return redirect('perfil')
   
    vaga = Vagas.objects.get(pk=nr_item)

    if request.method == 'GET':
        form = CadVagaForm(request.GET or None)

    elif request.method == 'POST':
        form = CadVagaForm(request.POST or None)     
        if vaga.status_vaga:
            vaga.status_vaga = False
            vaga.save()
            messages.success(request, 'Vaga desativada!')
        else: 
            vaga.status_vaga = True
            vaga.save()
            messages.success(request, 'Vaga ativada!')
        return redirect('administracao')

    return render(request, 'update/update_vaga_status.html', {'form': form})


# ALTERAÇÃO DUPLICAÇÃO DA VAGA
def DuplicateVagaAdmin(request, nr_item):
    if not request.user.is_authenticated:
        return redirect('entrar')
    
    if not request.user.is_admin:
        return redirect('perfil')

    vaga = Vagas.objects.get(pk=nr_item)
    
    if request.method == 'POST':
        cod = Vagas.objects.all().last().codigo_vaga
        Vagas(
            codigo_vaga=(int(cod) + 1),
            status_vaga=False,
            prioridade=vaga.prioridade,
            data_validade=vaga.data_validade,
            quantidade=vaga.quantidade,
            jornada=vaga.jornada,
            ensino=vaga.ensino,
            contratacao=vaga.contratacao,
            regiao=vaga.regiao,
            atividades=vaga.atividades,
            qualificacao=vaga.qualificacao,
            descricao=vaga.descricao,
            cargo=vaga.cargo,
            setor=vaga.setor
        ).save()
        messages.success(request, 'Vaga duplicada!')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
    return render(request, 'update/update_vaga_duplicar.html', {'vaga': vaga})


# ALTERAÇÃO DO VENCIMENTO DA VAGA
def UpdateVencVagaAdmin(request, nr_item):
    if not request.user.is_authenticated:
        return redirect('entrar')
    
    if not request.user.is_admin:
        return redirect('perfil')
    
    vaga = Vagas.objects.filter(pk=nr_item)
            
    if request.method == 'POST':
        data = request.POST.get('data_vencimento')
        Vagas.objects.filter(pk=nr_item).update(data_validade=data)
        messages.success(request, 'Data de vencimento alterada!')
        return redirect('administracao')
        
    return render(request, 'update/update_vaga_vencimento.html', {'vaga_venc': vaga})


# ALTERAÇÃO DE VAGA DO USUARIO
def UpdateVagaUsuarioAdmin(request, nr_item):
    if not request.user.is_authenticated:
        return redirect('entrar')
    
    if not request.user.is_admin:
        return redirect('perfil')
    
    vagauser = VagasUsuarios.objects.filter(id=nr_item)

    if request.method == 'POST':
        for s in request.POST.get('vagasuserup').split():
            if s.isdigit():
                cod = int(s)
        try:
            Vagas.objects.filter(codigo_vaga=cod)
            codx = Vagas.objects.get(codigo_vaga=cod).id
            vagauser.update(vaga_id=codx)
            messages.success(request, 'Vaga alterada!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        except:
            messages.success(request, 'Vaga não alterada!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return render(request, 'update/update_vaga_usuario.html', {'vagauser': vagauser})


# ALTERAÇÃO DE QUESTIONÁRIO
def UpdateQuestAdmin(request, nr_item):
    if not request.user.is_authenticated:
        return redirect('entrar')
    
    if not request.user.is_admin:
        return redirect('perfil')
    
    questionario = Questionario.objects.filter(id=nr_item)
    
    if request.method == 'POST':
        nota_nova = request.POST.get('pontuacao_questionario')   
        Questionario.objects.filter(id=nr_item).update(pontuacao_questionario=nota_nova)

    return render(request, 'update/update_questionario.html', {'questionario':questionario})


# ALTERAÇÃO DA FASE USUARIO
def UpdateFaseUsuario(request, nr_item):
    if not request.user.is_authenticated:
        return redirect('entrar')
    
    if not request.user.is_admin:
        return redirect('perfil')
    
    fase = FaseUsuario.objects.filter(pk=nr_item)
    value = FaseUsuario.objects.get(pk=nr_item).observacao
    
    if request.method == 'GET':
        form = CadUserFaseForm(request.GET or None)
        
    if request.method == 'POST':
       form = CadUserFaseForm(request.POST or None)
       obs = request.POST.get('observacao')
       if obs is not None and obs != []:
        fase = FaseUsuario.objects.filter(pk=nr_item).update(observacao=obs)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return render(request, 'update/update_fase_usuario.html', {'form':form, 'fase':fase, 'value': value})

#########################--CANDIDATO--#########################
from django.db import connections
def CandidatoView(request):
    if not request.user.is_authenticated:
        return redirect('entrar')
    
    if not request.user.is_admin:
        return redirect('perfil')

    if request.method == 'GET': 
        select      = render_to_string(os.path.join(base_dir, 'media\querysets\candidatos.sql'))
        codigo      = ""
        cpk         = ""
        status      = "(1,0)"
        nome        = "" 
        conditional = ""

        if request.GET.get('q') is not None and request.GET.get('q') != '':
            for s in request.GET.get('q').split():
                if s.isdigit():
                    codigo = int(s)
            cpk = Vagas.objects.get(codigo_vaga=codigo).pk
        
        if request.GET.get('q') is not None and request.GET.get('q') != '':
            if request.GET.get('p') == 'Ativado':
                status = "(1)"
            if request.GET.get('p') == 'Desativado':
                status = "(0)"
        
        if request.GET.get('r') is not None and request.GET.get('r') != '':
            nome = request.GET.get('r')
        
        conditional = ("where a.is_active = 1 and e.codigo_vaga like '%" + str(codigo) + "%' and a.status_cadastro in " + status + " and d.nome_completo like '%" + nome + "%'")
        select      = select.replace("where a.is_active = 1", conditional)
        
        cnn = connections['default'].cursor()
        with cnn as cursor:
            cursor.execute(select)
            coluna = [field_name[0] for field_name in cursor.description]
            candidatos = [dict(zip(coluna, linha)) for linha in cursor.fetchall()]
            cursor.close()
        cnn.close()
    
    if request.method == 'POST':    

        selecionados = request.POST.getlist('ids_selecionados')
        if selecionados is not None and selecionados != []:
            if request.POST.get('b1') == 'b1':
                VagasUsuarios.objects.filter(id__in=selecionados).update(is_active=False)   
            if request.POST.get('b2') == 'b2':
                for i in  selecionados:
                    VagasUsuarios.objects.filter(id=i).update(status_cadastro=True)
            if request.POST.get('b3') == 'b3':
                for i in selecionados:
                    usr = VagasUsuarios.objects.get(id=i).usuario
                    enviar_email_reprovacao(usr.id)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        ativar = request.POST.getlist('ativar_id')
        if ativar is not None and ativar != []:
            VagasUsuarios.objects.filter(id__in=ativar).update(status_cadastro=True)
            messages.success(request, 'Ativado!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        desativar = request.POST.getlist('desativar_id')
        if desativar is not None and desativar != []:
            VagasUsuarios.objects.filter(id__in=desativar).update(status_cadastro=False)
            messages.success(request, 'Desativado!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        aprovar = request.POST.get('email_aprovacao')
        if aprovar is not None:
            enviar_email_aprovacao(aprovar)
            messages.success(request, 'Email de aprovação enviado!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        dasaprovar = request.POST.get('email_reprovacao')
        if dasaprovar is not None:
            enviar_email_reprovacao(dasaprovar)
            messages.success(request, 'Email de reprovação enviado!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    page = request.GET.get('page', 1)
    paginator = Paginator(candidatos, 50)
    try:
        candidatos = paginator.page(page)
    except PageNotAnInteger:
        candidatos = paginator.page(1)
    except EmptyPage:
        candidatos = paginator.page(paginator.num_pages)
        
    return render(request, 'candidatos.html', {'vagas': Vagas.objects.filter(status_vaga=True), 'candidatos': candidatos, 'fases': Fase.objects.all()})