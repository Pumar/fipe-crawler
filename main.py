from crawler import App
from time import time
import logging


# class App:
#     logging.basicConfig(level=logging.INFO)
#     logger = logging.getLogger('App')
#
#     handler = logging.FileHandler('App.log')
#     handler.setLevel(logging.DEBUG)
#     formater = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#     handler.setFormatter(formater)
#     logger.addHandler(handler)
#
#     def __init__(self):
#         self.logger.info('criando App()')
#         self.options = Options()
#         self.options.add_argument('-headless')
#         self.logger.info('iniciano browser')
#         self.browser = webdriver.Firefox(
#             executable_path='C:/Users/Mobi2buy/PycharmProjects/fipe-crawler/firefox/geckodriver.exe',
#             firefox_options=self.options
#         )
#         self.logger.info('abrindo http://veiculos.fipe.org.br/')
#         self.browser.get("http://veiculos.fipe.org.br/")
#         self.logger.info('abrindo banco de dados')
#         self.database = Database()
#         self.reference_element = None
#         self.marca_element = None
#         self.modelo_element = None
#         self.ano_element = None
#         self.reference = None
#         self.marca = None
#         self.modelo = None
#         self.ano = None
#         self.logger.info('App() criado')
#
#     def restart_browser(self):
#         self.logger.info('encerrando browser')
#         self.browser.quit()
#         for i in range(1800):  # 1800 * 1 segundos == 30 minutos
#             self.logger.info('dormindo')
#             pause()
#         self.logger.info('reiniciano browser')
#         self.browser = webdriver.Firefox(
#             executable_path='C:/Users/Mobi2buy/PycharmProjects/fipe-crawler/firefox/geckodriver.exe',
#             firefox_options=self.options
#         )
#         self.logger.info('abrindo http://veiculos.fipe.org.br/')
#         self.browser.get("http://veiculos.fipe.org.br/")
#
#     def selection(self, div, input, text):
#         self.logger.info('inserindo {} text no input'.format(text))
#         div.click()
#         input.send_keys(text)
#         input.send_keys(Keys.ENTER)
#         pause()
#
#     def save_search(self):
#         self.logger.info('salvando busca')
#         self.browser.find_element_by_id('buttonPesquisarcarro').click()
#         self.logger.info('botão pesquisarclicado')
#         result = self.browser.find_element_by_id('resultadoConsultacarroFiltros')
#         self.logger.info('pegando valores dos campos')
#         table = result.find_element_by_tag_name('table')
#         info = table.find_elements_by_tag_name('td')
#         values = PageValues(info[5].text, info[7].text, info[9].text, info[15].text)
#         self.logger.info('valores da tabela pegos: {}'.format(values))
#         self.ano.codigo_fipe = info[3].text
#         self.ano.preco = info[15].text
#         self.logger.info('atualizando valores no banco de dados')
#         values.save_csv()
#         self.browser.find_element_by_id('buttonLimparPesquisarcarro').click()
#         self.logger.info('botão limpar busca clicado')
#         pause()
#         self.logger.info('pausa terminada')
#
#     def select_reference(self):
#         self.logger.info('selecionando mês de referência')
#         self.reference_element = Element(
#             self.browser.find_element_by_id('selectTabelaReferenciacarro_chosen'),
#             self.browser.find_element_by_id('selectTabelaReferenciacarro')
#         )
#         self.logger.info('Elemento reference criado')
#         self.database.save_reference(self.reference_element.texts)
#         self.logger.info('lista do combobox de referência salva no banco de dados')
#         while self.database.has_unvisited_reference():
#             self.logger.info('existe item no combobox não visitado')
#             self.reference = self.database.get_unvisted_reference()
#             self.logger.info('referencia pega no banco de dados: {}'.format(self.reference))
#             self.reference_element.div_click()
#             self.logger.info('div referencia clicada')
#             self.reference_element.selelct_by_index(self.reference.id - 1)
#             self.logger.info('selecionado o item {} do combobox'.format(self.reference.id - 1))
#             self.select_marca()
#             self.database.set_reference_visited(self.reference.id)
#             self.logger.info('reference atualizado para visitado {}'.format(self.reference.status))
#
#     def select_marca(self):
#         self.logger.info('selecionando marca')
#         self.marca_element = DataElement(
#             self.browser.find_element_by_id('selectMarcacarro_chosen'),
#             self.browser.find_element_by_id('selectMarcacarro')
#         )
#         self.logger.info('DataElement criado')
#
#         self.logger.info('consultando banco de dados para salvar as marcas')
#         if not self.database.has_marca_unvisited():
#             self.database.save_marcas(self.marca_element.texts, self.reference.id)
#
#         while self.database.has_marca_unvisited():
#             self.logger.info('marca não visitada')
#             self.marca = self.database.get_unvisted_marca()
#             self.logger.info('marca selecionada: {}'.format(self.marca.name))
#             self.marca_element.selection(self.marca.name)
#             self.logger.info('fazendo seleção da marca')
#             pause()
#             self.logger.info('pausa para load do ajax terminada')
#             self.select_modelo()
#             self.database.set_marca_visited(self.marca.id)
#             self.logger.info('marca {} marcada como visitada {}'.format(self.marca.name, self.marca.status))
#         self.logger.info('todos os modelos da marca {} foram visitados'.format(self.marca.name))
#
#     def select_modelo(self):
#         self.logger.info('selecionando modelo')
#         self.modelo_element = DataElement(
#             self.browser.find_element_by_id('selectAnoModelocarro_chosen'),
#             self.browser.find_element_by_id('selectAnoModelocarro')
#         )
#         self.logger.info('DataElement do modelo lido')
#
#         self.logger.info('checando banco de dados para salvar novos elementos')
#         if not self.database.has_unvisited_modelo():
#             self.database.save_modelos(self.modelo_element.texts, self.marca.id)
#         while self.database.has_unvisited_modelo():
#             self.logger.info('modelos não visitados')
#             self.modelo = self.database.get_unvisited_modelo()
#             self.logger.info('modelo selecionado do banco de dados: {}'.format(self.modelo.name))
#             self.marca_element.selection(self.marca.name)
#             self.logger.info('elemento marca selecionado')
#             self.modelo_element.selection(self.modelo.name)
#             self.logger.info('elemento modelo selecionado')
#             self.select_ano()
#             self.database.set_modelo_visited(self.modelo.id)
#             self.logger.info('modelo {} atualizado para visitado: {}'.format(self.modelo.name, self.modelo.status))
#         self.logger.info('não existe mais modelo a visitar')
#
#     def select_ano(self):
#         self.logger.info('selecionando ano do modelo')
#         self.ano_element = DataElement(
#             self.browser.find_element_by_id('selectAnocarro_chosen'),
#             self.browser.find_element_by_id('selectAnocarro')
#         )
#         self.logger.info('DataElement do ano criado')
#
#         self.logger.info('Verificando banco de dados para salvar novos itens')
#         if not self.database.has_unvisited_ano():
#             self.database.save_anos(self.ano_element.texts, self.modelo.id)
#
#         while self.database.has_unvisited_ano():
#             self.logger.info('Possui ano não visitado')
#             try:
#                 self.ano = self.database.get_unvisited_ano()
#                 self.logger.info('ano obtido do banco de dados: {}'.format(self.ano.ano_modelo))
#                 self.marca_element.selection(self.marca.name)
#                 self.logger.info('selecionando marca')
#                 self.modelo_element.selection(self.modelo.name)
#                 self.logger.info('selecionando modelo')
#                 self.ano_element.selection(self.ano.ano_modelo)
#                 self.logger.info('selecionando ano')
#                 self.save_search()
#                 self.logger.info('busca salva')
#                 self.database.set_ano_visited(self.ano.id)
#                 self.logger.info('ano {} marcado como visitado {}'.format(self.ano.ano_modelo, self.ano.status))
#             except Exception as error:
#                 self.logger.error('não foi possível selecionar os elementos {}'.format(error))
#                 self.restart_browser()
#         self.logger.info('Não possui anos não visitados')
#
#     def run(self):
#         self.browser.find_element_by_link_text('Consulta de Carros e Utilitários Pequenos').click()
#         self.select_reference()


if __name__ == '__main__':
    start = time()
    app = App()
    # app.run()
    try:
        app.run()
    except Exception as e:
        print(e)
        app.browser.quit()
    total = int(time() - start)
    second = total % 60
    minute = total // 60 % 60
    hour = total // 3600
    print('Running time: {}:{}:{}'.format(hour, minute, second))
