select distinct 
a.id                as id, 
a.is_active         as is_active, 
a.status_cadastro   as status, 
a.usuario_id        as usuario, 
d.nome_completo     as nome, 
h.name              as cidade, 
c.linkedin          as linkedin,
a.vaga_id           as vaga, 
e.codigo_vaga		as codigo_vaga,
g.nome_setor        as nome_setor, 
f.nome_cargo        as nome_cargo, 
a.data_cadastro     as data_cadastro, 
b.imagem            as imagem 

from        main_vagasusuarios  a 
left join   main_imagensperfil  b on a.usuario_id = b.usuario_id and b.imagem <> '' and b.id = (select max(id) from main_imagensperfil where usuario_id = a.usuario_id) 
left join   main_complementar   c on a.usuario_id = c.usuario_id and c.linkedin is not null 
left join   main_dadospessoais  d on a.usuario_id = d.usuario_id 
left join   main_vagas          e on a.vaga_id    = e.id 
left join   main_cargos         f on e.cargo_id   = f.id 
left join   main_setores        g on e.setor_id   = g.id 
left join   main_cidades        h on d.cidade_id  = h.id 

where a.is_active = 1

order by a.data_cadastro desc;