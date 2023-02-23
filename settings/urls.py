from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve 
from django.contrib.auth import views as auth_views
from main.views import (
    HomeView,
    RegistrationView,
    LoginView,
    LogoutView,
    ProfileView,
    
    VagasView,
    DetalhesVagaView,
    
    DadosPessoaisView, 
    FormacaoView, 
    DeleteFormacaoView,
    ExperienciaView, 
    DeleteExperienciaView,
    IdiomaView, 
    DeleteIdiomaView,
    TecnologiaView, 
    DeleteTecnologiaView,
    DadosComplementaresView,
    
    QuestionarioView,
    ArquivosView,
    ContatoView,
    AjudaView,
    TermoView,
    CookiesView,
    
    ResumeCurriculoView,
    ResumeVagasView,
    DeleteVagaView,
    )

from adm.views import (
    AdministracaoView,  
    CandidatoView,  
    
    CadReqAdmin,
    CadFaseAdmin,
    CadVagaAdmin,
    CadCargoAdmin,
    CadSetorAdmin,
    CadFaseUsuarioAdmin,
    
    RequisicaoAdmin,
    AprovaAdmin,
    CurriculoAdmin,
    ContasAdmin,
    CurriculosAdmin,
    DocumentosAdmin,
    QuestionariosAdmin,
    FasesAdmin,
    
    DelVagaAdmin,
    DelCargoAdmin,
    DelSetorAdmin,
    DelFaseAdmin,
    DelFaseUsuarioAdmin,
    
    UpdateReqAdmin,
    UpdateVagaAdmin,
    UpdateStatVagaAdmin,
    UpdateVencVagaAdmin,
    UpdateVagaUsuarioAdmin,
    UpdateQuestAdmin,
    UpdateFaseUsuario,    
    
    DuplicateVagaAdmin,
    )

urlpatterns = [    
    ###################################################################################################################################
    re_path(r'^ckeditor/', include('ckeditor_uploader.urls')),
	re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}), 
	re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}), 

    path('admin/', admin.site.urls),
    path('', HomeView, name="home"),
    path('registrar/', RegistrationView, name="registrar"),
    path('entrar/', LoginView, name="entrar"),
    path('sair/', LogoutView, name="sair"),
    
    path('perfil/', ProfileView, name="perfil"),
    
    path('perfil/meu_curriculo', ResumeCurriculoView, name="meu_curriculo"),
    path('perfil/minhas_vagas', ResumeVagasView, name="minhas_vagas"),
    path('perfil/minhas_vagas/deletar_vaga/<nr_item>', DeleteVagaView, name="deletar_vaga"),
    
    path('perfil/enviar/arquivos', ArquivosView, name="arquivos"),
    path('perfil/ajuda', AjudaView, name="ajuda"),
    path('contato', ContatoView, name="contato"),
    path('termo', TermoView, name="termo"),
    path('politica_de_cookies', CookiesView, name="politica_de_cookies"),
    
    path('vagas/', VagasView, name="vagas"),
    path('vagas/detalhes_vaga/<nr_item>', DetalhesVagaView, name="detalhes_vaga"),
    
    path('perfil/cadastrar/dados_pessoais', DadosPessoaisView, name="dados_pessoais"),
    path('perfil/cadastrar/formacoes_academicas', FormacaoView, name="formacoes_academicas"),
    path('perfil/excluir/formacao/<nr_item>', DeleteFormacaoView, name="deletar_formacao"),
    path('perfil/cadastrar/experiencias_profissionais', ExperienciaView, name="experiencias_profissionais"),
    path('perfil/excluir/experiencia/<nr_item>', DeleteExperienciaView, name="deletar_experiencia"),
    path('perfil/cadastrar/idiomas', IdiomaView, name="idiomas"),
    path('perfil/excluir/idioma/<nr_item>', DeleteIdiomaView, name="deletar_idioma"),
    path('perfil/cadastrar/tecnologias', TecnologiaView, name="tecnologias"),
    path('perfil/excluir/tecnologia/<nr_item>', DeleteTecnologiaView, name="deletar_tecnologia"),
    path('perfil/cadastrar/dados_complementares', DadosComplementaresView, name="dados_complementares"),
    path('perfil/cadastrar/questionario', QuestionarioView, name="questionario"),
    
    
    path('recuperar_senha/', auth_views.PasswordResetView.as_view(), name='password_reset'),    
    path('recuperar_senha/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('perfil/alterar_senha', auth_views.PasswordChangeView.as_view(template_name='registration/password_change.html'), name='password_change'),
    ###################################################################################################################################
    
    #URL INICIAL
    path('administracao', AdministracaoView, name="administracao"),
    path('administracao/candidatos', CandidatoView, name="candidatos"),

    #URLS DE CADASTRO
    path('administracao/cadastrar/requisicao', CadReqAdmin, name="cadastrar_requisicao"),
    path('administracao/cadastrar/vagas', CadVagaAdmin, name="cadastrar_vagas"),
    path('administracao/cadastrar/cargos', CadCargoAdmin, name="cadastrar_cargos"),
    path('administracao/cadastrar/setores', CadSetorAdmin, name="cadastrar_setores"),
    path('administracao/cadastrar/fases', CadFaseAdmin, name="cadastrar_fases"),
    path('administracao/cadastrar/fases_usuario/<nr_item>', CadFaseUsuarioAdmin, name="cadastrar_faseusuaurio"),
       
    #URLS DE VISUALIZAÇÃO
    path('administracao/visualizar/requisicoes', RequisicaoAdmin, name="requisicoes"),
    path('administracao/visualizar/aprovacao/requisicoes', AprovaAdmin, name="aprovacoes"),
    path('administracao/visualizar/curriculo/pdf/<nr_item>', CurriculoAdmin, name="curriculo"),
    path('administracao/visualizar/contas', ContasAdmin, name="contas"),
    path('administracao/visualizar/curriculos', CurriculosAdmin, name="curriculos"),
    path('administracao/visualizar/documentos', DocumentosAdmin, name="documentos"),
    path('administracao/visualizar/questionarios', QuestionariosAdmin, name="questionarios"),
    path('administracao/visualizar/fases', FasesAdmin, name="fases"),
    
    #URLS DE EXCLUSÃO
    path('administracao/deletar/vaga/<nr_item>', DelVagaAdmin, name="deletar_vaga"),
    path('administracao/deletar/cargo/<nr_item>', DelCargoAdmin, name="deletar_cargo"),
    path('administracao/deletar/setor/<nr_item>', DelSetorAdmin, name="deletar_setor"),
    path('administracao/deletar/fase/<nr_item>', DelFaseAdmin, name="deletar_fase"),
    path('administracao/deletar/fase_usuario/<nr_item>', DelFaseUsuarioAdmin, name="deletar_fase_usuario"),
    
    #URLS DE ALTERAÇÃO    
    path('administracao/update/requisicao/<nr_item>', UpdateReqAdmin, name="alterar_requisicao"),
    path('administracao/update/vaga/<nr_item>', UpdateVagaAdmin, name="alterar_vaga"),
    path('administracao/update/vaga/status/<nr_item>', UpdateStatVagaAdmin, name="update_vaga"),
    path('administracao/update/vaga/vencimento/<nr_item>', UpdateVencVagaAdmin, name="vencimento_vaga"),
    path('administracao/update/vagausuario/<nr_item>', UpdateVagaUsuarioAdmin, name="alterar_vagausuario"),
    path('administracao/update/questionario/<nr_item>', UpdateQuestAdmin, name="alterar_questionario"),
    path('administracao/update/faseusuario/<nr_item>', UpdateFaseUsuario, name="alterar_faseusuario"),
    
    #URLS DE DUPLICAÇÃO
    path('administracao/duplicar/vaga/<nr_item>', DuplicateVagaAdmin, name="duplicate_vaga"),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)