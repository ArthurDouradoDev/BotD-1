# Fase Inicial

1- Acessar o site https://microstrategyqualidade.internal.timbrasil.com.br/MicroStrategy/servlet/mstrWeb?continue

Sera redirecionado para um login da microsoft:
login: T3755000@timbrasil.com.br
senha: xxxx

2- Aprovacao com Authenticator

3- Redirecionado de volta para https://microstrategyqualidade.internal.timbrasil.com.br/MicroStrategy/servlet/mstrWeb?continue

4- Clica em:
<a onclick="return submitLink(this, event);" href="mstrWeb?evt=3010&amp;src=mstrWeb.3010&amp;loginReq=true&amp;Server=10.98.4.18&amp;ServerAlias=10.98.4.18&amp;Project=QualiTim&amp;Port=0" class="mstrLargeIconViewItemLink"></a>

5- A pagina aberta sera um painel. Clica em: <div class="mstr-dskt-nm">My Subscriptions</div>

6- Sera aberta a lista de planilhas em outra pagina. La tera a opcao para acessar as planilhas.

--- Nessa pagina, terao três fluxos
## A) Acessar o 4G:
1- Clica em <td cmd="tgt" class="mstrLink">D-1 OFENSORES 4G</td>
2- E direcionado para uma pagina de carregamento
3- E redirecionado para a pagina da tabela
4- Clica em <div class="">Report Home</div>
5- Clica em <a class="mstrToolbarButton" style="display: block;"><span id="tbExport" style="" align="absmiddle" onmouseout="mstr.behaviors.ToolbarButton.setButtonClassName(mstr.$obj('id_mstr85'), false);" onmouseover="mstr.behaviors.ToolbarButton.setButtonClassName(mstr.$obj('id_mstr85'), true);" onclick="var v = mstr.$obj('id_mstr85'); if (v.get('enabled')) { v.fireCommands() } return false;" title="Export"></span></a>
6- Uma nova aba sera aberta e o download e feito
7- Sai do 4G clicando em <a onclick="return submitLinkAsFormWithoutState(this);" href="mstrWeb?evt=3010&amp;src=mstrWeb.3010&amp;Server=10.98.4.18&amp;Project=QualiTim&amp;Port=0" class="mstrLink">QualiTim</a>
-> Nesse momento, retorna para a tela anterior ao mysubscriptions ( antes do passo 5 do original). Deve clicar em: <div class="mstr-dskt-nm">My Subscriptions</div>


## B) Acessar o 5G:
1- Clica em <td cmd="tgt" class="mstrLink">D-1 OFENSORES 5G</td>
2- E direcionado para uma pagina de carregamento
3- E redirecionado para a pagina da tabela
4- Clica em <div class="">Report Home</div>
5- Clica em <a class="mstrToolbarButton" style="display: block;"><span id="tbExport" style="" align="absmiddle" onmouseout="mstr.behaviors.ToolbarButton.setButtonClassName(mstr.$obj('id_mstr85'), false);" onmouseover="mstr.behaviors.ToolbarButton.setButtonClassName(mstr.$obj('id_mstr85'), true);" onclick="var v = mstr.$obj('id_mstr85'); if (v.get('enabled')) { v.fireCommands() } return false;" title="Export"></span></a>
6- Uma nova aba sera aberta e o download e feito
7- Sai do 5G clicando em <a onclick="return submitLinkAsFormWithoutState(this);" href="mstrWeb?evt=3010&amp;src=mstrWeb.3010&amp;Server=10.98.4.18&amp;Project=QualiTim&amp;Port=0" class="mstrLink">QualiTim</a>
-> Nesse momento, retorna para a tela anterior ao mysubscriptions ( antes do passo 5 do original). Deve clicar em: <div class="mstr-dskt-nm">My Subscriptions</div>

## C) Acessar o 3G:
1- Clica em <td cmd="tgt" class="mstrLink">Otimização por Célula 3G - Diário- D-1 SP - Huawei</td>
2- Clica no elemento <td class="right menu"></td> que fica na div <div class="mstrListBlockToolbarItemSelected" title="" style="display: block;"><table cellspacing="0"><tbody><tr><td class="left"></td><td class="mstrListBlockToolbarItemName"><div class="">Data</div></td><td class="right menu"></td></tr></tbody></table></div>
3- Clica em <span>Re-prompt</span>
4- Clica no input <input maxlength="" onblur="return mstr.behaviors.CalendarAndTimePicker.onblur_dayinput('id_mstr111',this,arguments[0]);" onkeypress="if (!mstr.utils.ISW3C) return mstr.behaviors.CalendarAndTimePicker.onkeypress_dayinput('id_mstr111','id_mstr111_txt', arguments[0]);" onkeydown="if (mstr.utils.ISW3C)return mstr.behaviors.CalendarAndTimePicker.onkeypress_dayinput('id_mstr111','id_mstr111_txt',arguments[0]);" name="id_mstr111_txt" style="display: block; background-color: rgb(255, 255, 255);" id="id_mstr111_txt" size="22" type="text" title="">
5- Substitui o conteudo do input pela data do D-1, digitando no formato dd/mm/yyyy
6- Clica em <input style="display: inline; cursor: pointer;" title="" class="mstrButton" id="id_mstr155" value="Run Report" type="button" onclick="return mstr.$obj(this.id).fireCommands()">
7- Clica novamente me <input style="display: inline; cursor: pointer;" title="" class="mstrButton" id="id_mstr155" value="Run Report" type="button" onclick="return mstr.$obj(this.id).fireCommands()">
8- Clica em <div class="">Report Home</div>
9- Clica em <a class="mstrToolbarButton" style="display: block;"><span id="tbExport" style="" align="absmiddle" onmouseout="mstr.behaviors.ToolbarButton.setButtonClassName(mstr.$obj('id_mstr85'), false);" onmouseover="mstr.behaviors.ToolbarButton.setButtonClassName(mstr.$obj('id_mstr85'), true);" onclick="var v = mstr.$obj('id_mstr85'); if (v.get('enabled')) { v.fireCommands() } return false;" title="Export"></span></a>
10- Uma nova aba sera aberta e o download e feito