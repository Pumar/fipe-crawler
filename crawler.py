import csv
import time
import logging
import configparser
import os

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from db_declarative import Reference, ReferenceHasMarca, Marca, Modelo, AnoModelo, Base, Status

from time import sleep


UNVISITED = 1
VISITED = 2
ERROR = 3

path = os.path.dirname(os.path.abspath(__file__))

config = configparser.ConfigParser()
config.read('config.ini')
MainDivName = config['DivVehicleDesc']['MainDivName']
filename = config['VehicleType']['filename']
vehicle = config['VehicleType']['vehicle']

class PageValues:
    def __init__(self, marca, modelo, ano_modelo, preco):
        """
        PageValues is started with values that will be saved in csv file.
        :param marca: product name in the web page
        :param modelo: web page title
        :param ano_modelo: product url
        :type ano_modelo: str
        :type modelo: str
        :type marca: str
        """
        # this dictionary will be used to save data in csv file
        self.__values = {
            'marca': marca,
            'modelo': modelo,
            'anoModelo': ano_modelo,
            'preco': preco
        }
        # __csv_fields make save_data() method writes correctly in csv file.
        self.__csv_fields = self.__values.keys()
        self.__csv_file_name = filename

    @property
    def marca(self):
        """
        Returns the url of a product
        :rtype: str
        """
        return self.__values['marca']

    @property
    def modelo(self):
        """
        Returns the product web page title
        :rtype: str
        """
        return self.__values['modelo']

    @property
    def ano_modelo(self):
        """
        Returns the product name
        :rtype: str
        """
        return self.__values['anoModelo']

    @property
    def preco(self):
        return self.__values['preco']

    def __is_csv(self):
        """
        Checks if the csv file already exists.
        Returns true if there is the csv file, and false if not.
        :rtype: bool
        """
        try:
            # just open to check if there is the file
            with open(self.__csv_file_name, 'r') as file:
                file.close()
            return True
        # if it do not exists the exception will returns false
        except IOError:
            return False

    def __create_csv(self):
        """
        Creates a csv file.
        Writes in the file the fields of each attributes.
        """
        with open(self.__csv_file_name, 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.__csv_fields, delimiter=';')
            writer.writeheader()

    def save_csv(self):
        """
        Checks if the csv file already exists to write in it the
        product name, his title web page and his url.
        """
        if not self.__is_csv():
            # creates the csv file if it did not exist.
            self.__create_csv()
        try:
            with open(self.__csv_file_name, 'a', newline='', encoding='utf-8') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=self.__csv_fields, delimiter=';')
                writer.writerow(self.__values)
        except IOError:  # this exception avoid a product does not have saved in csv file
            sleep(0.5)
            self.save_csv()
        # display on the screen what is being record on csv
        for key, value in self.__values.items():
            print('{}: {}'.format(key, value), end='; ' if key != 'preco' else '\n')

    def __str__(self):
        return 'PageValues: (marca: {}, modelo: {}, ano_modelo: {}, preco:{}'.format(
            self.marca, self.modelo, self.ano_modelo, self.preco
        )


class Element:
    def __init__(self, div, select):
        self.div = div  # browser.find_element_by_id('selectTabelaReferencia'+vehicle+'_chosen')
        self.element = select  # browser.find_element_by_id('selectTabelaReferencia'+vehicle)
        self.select = Select(self.element)
        self.options = [x for x in self.element.find_elements_by_tag_name('option')]
        self.texts = [r.get_attribute('innerHTML').replace('&amp;', '&') for r in self.options]

    def div_click(self):
        self.div.click()

    def selelct_by_index(self, index):
        self.select.select_by_index(index)


class DataElement(Element):
    def __init__(self, div, select):
        super(DataElement, self).__init__(div, select)
        self.input = self.div.find_element_by_tag_name('input')

    def input_send(self, keys):
        self.input.send_keys(keys)
        self.input.send_keys(Keys.ENTER)

    def selection(self, text):
        self.div_click()
        self.input_send(text)
        pause()


class Database:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('DATABASE')

    handler = logging.FileHandler('database.log')
    handler.setLevel(logging.DEBUG)
    formater = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formater)
    logger.addHandler(handler)

    engine = create_engine('sqlite:///fipe.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    def save_database(self, data):
        try:
            self.logger.info('save_database {}'.format(str(data)))
            self.session.add(data)
            self.session.commit()
        except Exception as error:
            self.logger.error('save database {} {}'.format(data, error))
            pause()
            self.save_database(data)

    def save_reference(self, reference_list):
        self.logger.info('save_reference {}'.format(str(reference_list)))
        if self.has_unvisited_reference() or self.reference_count() == 0:
            for period in reference_list:
                self.logger.info('period: {}'.format(period))
                if self.has_not_reference(period):
                    reference = Reference(period=period)
                    self.save_database(reference)

    def reference_count(self):
        self.logger.info('has_reference')
        query = self.session.query(Reference).count()
        self.logger.info('has_reference {}'.format(query))
        return query

    def has_not_reference(self, period):
        self.logger.info('has_not_reference {}'.format(str(period)))
        query = self.session.query(Reference).filter(Reference.period == period).count()
        self.logger.info('has_not_reference {} {}'.format(period, True if query == 0 else False))
        if query == 0:
            return True
        return False

    def has_unvisited_reference(self):
        self.logger.info('has_unvisited_reference')
        query = self.session.query(Reference).filter(Reference.status == UNVISITED).count()
        self.logger.info('has_unvisited_reference {}'.format(True if query > 0 else False))
        if query > 0:
            return True
        return False

    def get_unvisted_reference(self):
        self.logger.info('has_unvisited_reference')
        query = self.session.query(Reference).filter(Reference.status == UNVISITED).all()
        self.logger.info('has_unvisited_reference {}'.format(query))
        return query[0]

    def has_marca_unvisited(self):
        self.logger.info('has_marca_unvisited')
        query = self.session.query(Marca).filter(Marca.status == UNVISITED).count()
        self.logger.info('has_query_unvisited'.format(True if query > 0 else False))
        if query > 0:
            return True
        return False

    def has_marca(self, name):
        self.logger.info('has_marca {}'.format(name))
        query = self.session.query(Marca).filter(Marca.name == name).count()
        self.logger.info('has_marca {} - {}'.format(name, True if query > 0 else False))
        if query > 0:
            return True
        return False

    def set_unvisited_marca(self, name):
        self.logger.info('set_marca_unvisited {}'.format(name))
        marca = self.session.query(Marca).filter(Marca.name == name).one()
        marca.status = UNVISITED
        self.save_database(marca)
        self.logger.info('set_marca_unvisited {}'.format(marca.status))

    def get_marca_id(self, name):
        self.logger.info('get_marca_id {}'.format(name))
        query = self.session.query(Marca).filter(Marca.name == name).one()
        self.logger.info('get_marca_id {}'.format(query.id))
        return query.id

    def save_marcas(self, marca_list, reference_id):
        self.logger.info('save_marca {} - {}'.format(reference_id, marca_list))
        for marca in marca_list:
            self.logger.info('for marca in marca_list: {}'.format(marca))
            if self.has_marca(marca):
                self.logger.info('setting unvisited marca {}'.format(marca))
                self.set_unvisited_marca(marca)
                marca_id = self.get_marca_id(marca)
            else:
                self.logger.info('new marca {}'.format(marca))
                new_marca = Marca(name=marca)
                self.save_database(new_marca)
                marca_id = new_marca.id
            reference_marca = ReferenceHasMarca(reference_id=reference_id, marca_id=marca_id)
            self.save_database(reference_marca)

    def get_unvisted_marca(self):
        self.logger.info('get_unvisited_marca')
        query = self.session.query(Marca).filter(Marca.status == UNVISITED).all()
        self.logger.info('get_unvisited_marca {}'.format(query[0]))
        return query[0]

    def save_modelos(self, modelo_list, marca_id):
        self.logger.info('save_modelos {} {}'.format(marca_id, modelo_list))
        for modelo in modelo_list:
            if self.has_modelo(modelo):
                self.logger.info('has modelo {}'.format(modelo))
                self.logger.info('setting unvisited modelo {}'.format(modelo))
                self.set_unvisted_modelo(modelo)
            else:
                self.logger.info('new modelo {}'.format(modelo))
                self.logger.info('hasn\'t modelo')
                new_modelo = Modelo(name=modelo, marca_id=marca_id)
                self.save_database(new_modelo)

    def has_modelo(self, name):
        self.logger.info('has_modelo {}'.format(name))
        query = self.session.query(Modelo).filter(Modelo.name == name).count()
        self.logger.info('has_modelo {} {}'.format(name, True if query > 0 else False))
        if query > 0:
            return True
        return False

    def set_unvisted_modelo(self, name):
        self.logger.info('set_unvisited_modelo {}'.format(name))
        modelo = self.session.query(Modelo).filter(Modelo.name == name).one()
        modelo.status = UNVISITED
        self.save_database(modelo)
        self.logger.info('set_unvisited_modelo {} {}'.format(modelo.name, modelo.id))

    def has_unvisited_modelo(self):
        self.logger.info('has_unvisited_modelo')
        query = self.session.query(Modelo).filter(Modelo.status == UNVISITED).count()
        self.logger.info('has_unvisited_modelo {}'.format(True if query > 0 else False))
        if query > 0:
            return True
        return False

    def get_unvisited_modelo(self):
        self.logger.info('get_unvisited_modelo')
        query = self.session.query(Modelo).filter(Modelo.status == UNVISITED).all()
        self.logger.info('get_unvisited_modelo {}'.format(query[0]))
        return query[0]

    def has_unvisited_ano(self):
        self.logger.info('has_unvisited_ano')
        query = self.session.query(AnoModelo).filter(AnoModelo.status == UNVISITED).count()
        self.logger.info('has_unvisited_ano {}'.format(True if query > 0 else False))
        if query > 0:
            return True
        return False

    def save_anos(self, ano_list, modelo_id):
        self.logger.info('save_anos {} {}'.format(modelo_id, ano_list))
        for ano in ano_list:
            self.logger.info('new ano {}'.format(ano))
            new_ano = AnoModelo(ano_modelo=ano, modelo_id=modelo_id)
            self.save_database(new_ano)

    def has_ano(self, ano):
        self.logger.info('has_ano {}'.format(ano))
        query = self.session.query(AnoModelo).filter(AnoModelo.ano_modelo == ano).count()
        self.logger.info('has_ano {} {} {}'.format(ano.id, ano.ano_modelo, True if query > 0 else False))
        if query > 0:
            return True
        return False

    def set_unvisited_ano(self, ano):
        self.logger.info('set_unvisited_ano {}'.format(ano))
        ano = self.session.query(AnoModelo).filter(AnoModelo.ano_modelo == ano).one()
        ano.status = UNVISITED
        self.save_database(ano)
        self.logger.info('set_unvisited_ano {} {}'.format(ano.ano_modelo, ano.status))

    def get_unvisited_ano(self):
        self.logger.info('get_unvisited_ano')
        query = self.session.query(AnoModelo).filter(AnoModelo.status == UNVISITED).all()
        self.logger.info('get_unvisited_ano {}'.format(query[0].ano_modelo))
        return query[0]

    def set_modelo_visited(self, id):
        self.logger.info('set_modelo_visited {}'.format(id))
        modelo = self.session.query(Modelo).filter(Modelo.id == id).one()
        modelo.status = VISITED
        self.save_database(modelo)
        self.logger.info('set_modelo_visited {} {}'.format(modelo.name, modelo.status))

    def set_ano_visited(self, id):
        self.logger.info('set_ano_visited {}'.format(id))
        ano = self.session.query(AnoModelo).filter(AnoModelo.id == id).one()
        ano.status = VISITED
        self.save_database(ano)
        self.logger.info('set_ano_visited {} {}'.format(ano.ano_modelo, ano.status))

    def set_marca_visited(self, id):
        self.logger.info('set_marca_visited {}'.format(id))
        marca = self.session.query(Marca).filter(Marca.id == id).one()
        marca.status = VISITED
        self.save_database(marca)
        self.logger.info('set_marca_visited {} {}'.format(marca.name, marca.status))

    def set_reference_visited(self, id):
        self.logger.info('set_reference_visited {}'.format(id))
        ref = self.session.query(Reference).filter(Reference.id == id).one()
        ref.status = VISITED
        self.save_database(ref)
        self.logger.info('set_reference_visited {} {}'.format(ref.name, ref.status))


class App:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('App')

    handler = logging.FileHandler('App.log')
    handler.setLevel(logging.DEBUG)
    formater = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formater)
    logger.addHandler(handler)

    def __init__(self):
        self.logger.info('criando App()')
        self.options = Options()
        self.options.add_argument('-headless')
        self.logger.info('iniciano browser')
        self.browser = webdriver.Firefox(
            executable_path=path+'firefox/geckodriver.exe',
            firefox_options=self.options
        )
        self.logger.info('abrindo http://veiculos.fipe.org.br/')
        self.browser.get("http://veiculos.fipe.org.br/")
        self.logger.info('abrindo banco de dados')
        self.database = Database()
        self.reference_element = None
        self.marca_element = None
        self.modelo_element = None
        self.ano_element = None
        self.reference = None
        self.marca = None
        self.modelo = None
        self.ano = None
        self.logger.info('App() criado')

    def restart_browser(self):
        self.logger.info('encerrando browser')
        self.browser.quit()
        self.logger.info('dormindo')
        for i in range(1800):  # 1800 * 1 segundos == 30 minutos
            pause()
        self.logger.info('reiniciano browser')
        self.browser = webdriver.Firefox(
            executable_path=path+'firefox/geckodriver.exe',
            firefox_options=self.options
        )
        self.logger.info('abrindo http://veiculos.fipe.org.br/')
        try:
            self.browser.get("http://veiculos.fipe.org.br/")
            self.browser.find_element_by_link_text(MainDivName).click()
        except Exception as err:
            self.logger.error(err)
            self.restart_browser()

    def selection(self, div, input, text):
        self.logger.info('inserindo {} text no input'.format(text))
        div.click()
        input.send_keys(text)
        input.send_keys(Keys.ENTER)
        pause()

    def save_search(self):
        self.logger.info('salvando busca')
        self.browser.find_element_by_id('buttonPesquisar'+vehicle).click()
        self.logger.info('botão pesquisarclicado')
        result = self.browser.find_element_by_id('resultadoConsulta'+vehicle+'Filtros')
        self.logger.info('pegando valores dos campos')
        table = result.find_element_by_tag_name('table')
        info = table.find_elements_by_tag_name('td')
        values = PageValues(info[5].text, info[7].text, info[9].text, info[15].text)
        self.logger.info('valores da tabela pegos: {}'.format(values))
        self.ano.codigo_fipe = info[3].text
        self.ano.preco = info[15].text
        self.logger.info('atualizando valores no banco de dados')
        values.save_csv()
        self.browser.find_element_by_id('buttonLimparPesquisar'+vehicle).click()
        self.logger.info('botão limpar busca clicado')
        pause()
        self.logger.info('pausa terminada')

    def select_reference(self):
        self.logger.info('selecionando mês de referência')
        self.reference_element = Element(
            self.browser.find_element_by_id('selectTabelaReferencia'+vehicle+'_chosen'),
            self.browser.find_element_by_id('selectTabelaReferencia'+vehicle)
        )
        self.logger.info('Elemento reference criado')
        self.database.save_reference(self.reference_element.texts)
        self.logger.info('lista do combobox de referência salva no banco de dados')
        while self.database.has_unvisited_reference():
            self.logger.info('existe item no combobox não visitado')
            self.reference = self.database.get_unvisted_reference()
            self.logger.info('referencia pega no banco de dados: {}'.format(self.reference))
            self.reference_element.div_click()
            self.logger.info('div referencia clicada')
            self.reference_element.selelct_by_index(self.reference.id - 1)
            self.logger.info('selecionado o item {} do combobox'.format(self.reference.id - 1))
            self.select_marca()
            self.database.set_reference_visited(self.reference.id)
            self.logger.info('reference atualizado para visitado {}'.format(self.reference.status))

    def select_marca(self):
        self.logger.info('selecionando marca')
        self.marca_element = DataElement(
            self.browser.find_element_by_id('selectMarca'+vehicle+'_chosen'),
            self.browser.find_element_by_id('selectMarca'+vehicle)
        )
        self.logger.info('DataElement criado')

        self.logger.info('consultando banco de dados para salvar as marcas')
        if not self.database.has_marca_unvisited():
            self.database.save_marcas(self.marca_element.texts, self.reference.id)

        while self.database.has_marca_unvisited():
            self.logger.info('marca não visitada')
            self.marca = self.database.get_unvisted_marca()
            self.logger.info('marca selecionada: {}'.format(self.marca.name))
            self.marca_element.selection(self.marca.name)
            self.logger.info('fazendo seleção da marca')
            pause()
            self.logger.info('pausa para load do ajax terminada')
            self.select_modelo()
            self.database.set_marca_visited(self.marca.id)
            self.logger.info('marca {} marcada como visitada {}'.format(self.marca.name, self.marca.status))
        self.logger.info('todos os modelos da marca {} foram visitados'.format(self.marca.name))

    def select_modelo(self):
        self.logger.info('selecionando modelo')
        self.modelo_element = DataElement(
            self.browser.find_element_by_id('selectAnoModelo'+vehicle+'_chosen'),
            self.browser.find_element_by_id('selectAnoModelo'+vehicle)
        )
        self.logger.info('DataElement do modelo lido')

        self.logger.info('checando banco de dados para salvar novos elementos')
        if not self.database.has_unvisited_modelo():
            self.database.save_modelos(self.modelo_element.texts, self.marca.id)
        while self.database.has_unvisited_modelo():
            self.logger.info('modelos não visitados')
            self.modelo = self.database.get_unvisited_modelo()
            self.logger.info('modelo selecionado do banco de dados: {}'.format(self.modelo.name))
            self.marca_element.selection(self.marca.name)
            self.logger.info('elemento marca selecionado')
            self.modelo_element.selection(self.modelo.name)
            self.logger.info('elemento modelo selecionado')
            self.select_ano()
            self.database.set_modelo_visited(self.modelo.id)
            self.logger.info('modelo {} atualizado para visitado: {}'.format(self.modelo.name, self.modelo.status))
        self.logger.info('não existe mais modelo a visitar')

    def select_ano(self):
        self.logger.info('selecionando ano do modelo')
        self.ano_element = DataElement(
            self.browser.find_element_by_id('selectAno'+vehicle+'_chosen'),
            self.browser.find_element_by_id('selectAno'+vehicle)
        )
        self.logger.info('DataElement do ano criado')

        self.logger.info('Verificando banco de dados para salvar novos itens')
        if not self.database.has_unvisited_ano():
            self.database.save_anos(self.ano_element.texts, self.modelo.id)

        while self.database.has_unvisited_ano():
            self.logger.info('Possui ano não visitado')
            try:
                self.ano = self.database.get_unvisited_ano()
                self.logger.info('ano obtido do banco de dados: {}'.format(self.ano.ano_modelo))
                self.marca_element.selection(self.marca.name)
                self.logger.info('selecionando marca')
                self.modelo_element.selection(self.modelo.name)
                self.logger.info('selecionando modelo')
                self.ano_element.selection(self.ano.ano_modelo)
                self.logger.info('selecionando ano')
                self.save_search()
                self.logger.info('busca salva')
                self.database.set_ano_visited(self.ano.id)
                self.logger.info('ano {} marcado como visitado {}'.format(self.ano.ano_modelo, self.ano.status))
            except Exception as error:
                self.logger.error('não foi possível selecionar os elementos {}'.format(error))
                self.restart_browser()
        self.logger.info('Não possui anos não visitados')

    def run(self):
        self.browser.find_element_by_link_text(MainDivName).click()
        self.select_reference()

#Change to game crawler detection, might have to use randint
def pause():
    sleep(1)


if __name__ == '__main__':
    start = time.time()
    app = App()
    # app.run()
    try:
        app.run()
    except Exception as e:
        print(e)
        app.browser.quit()
    total = int(time.time() - start)
    second = total % 60
    minute = total // 60 % 60
    hour = total // 3600
    print('{}:{}:{}'.format(hour, minute, second))
