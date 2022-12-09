import gspread
from django.conf import settings
import os
import json
from django.core import serializers

def addicionar(self):
    adr = [self.pk,str(serializers.serialize('json', [self]))]
    ad = str(serializers.serialize('json', [self])).split("[")
    ad = str(ad[1]).split("]")
    ad = json.loads(str(ad[0]))
    ad = str(ad['model']).split('.')
    return adr, str(ad[1])


class Sheets:

    def __init__(self):
        url = f'{settings.BASE_DIR}/service_account.json'
        gc = gspread.service_account(url)
        self.sh = gc.open_by_key(settings.SHEETS_KEY)
        self.worksheet = self.sh.worksheet(settings.SHEETS_WORK)
        self.SHEETS_WORK = settings.SHEETS_WORK
    def ler(self,range=None,worksheet=None):
        if worksheet == None:
            return self.worksheet.get_all_values()
        else:
            worksheet = self.sh.worksheet(worksheet)
            return worksheet.get_all_values()


    def lertabmod(self,se):
        ws = str(se)
        worksheet = self.sh.worksheet(ws)
        lis = []
        for li in worksheet.col_values(2):
            s = li.split("[")
            s = s[1].split("]")
            lis.append(s[0])
        lis = str(lis)
        lista = lis.replace("['",'[')
        lista = lista.replace("']",']')
        lista = lista.replace("'",'')
        return json.loads(lista)


    def verificarigualdade(self,se,worksheet=None):
        antigo = se.pk
        add, worksheet = addicionar(se)
        x = 1
        y = False
        worksheet = self.sh.worksheet(worksheet)
        itens = worksheet.col_values(2)
        itensfiltrados = []
        for i in itens:
            if not (i in itensfiltrados):
                itensfiltrados.append(i)
        #self.worksheet.delete_rows(1, len(self.worksheet.col_values(1)))
        for i in itensfiltrados:
            ad = str(i).split("[")
            ad = str(ad[1]).split("]")
            ad = json.loads(str(ad[0]))
            adr = [ad['pk'], i]
            self.sh.values_append(f'{worksheet}!A1', params={'valueInputOption': 'RAW'}, body={'values': [adr]})
        if not (add in itensfiltrados):
            y = True
        return y

    def adicionar(self,se):
        print(self.verificarigualdade(se))
        if self.verificarigualdade(se) == True:
            print("TRUE")
            add, worksheet = addicionar(se)
            if worksheet == None:
                self.sh.values_append(f'{self.SHEETS_WORK}!A1', params={'valueInputOption': 'RAW'}, body={'values': [add]})
            else:
                self.sh.values_append(f'{worksheet}!A1', params={'valueInputOption': 'RAW'}, body={'values': [add]})
                return self.ler(worksheet=worksheet)
            return self.ler()

    def updata(self,se,antigo=None,worksheet=None):
        if self.verificarigualdade(se) == True:
            antigo = se.pk
            add, worksheet = addicionar(se)
            x = 1
            y = None
            if worksheet == None:
                pks = self.worksheet.col_values(1)
            else:
                worksheet = self.sh.worksheet(worksheet)
                pks = worksheet.col_values(1)
            for i in pks:
                if int(i) == int(antigo):
                    y = x
                x += 1
            if y == None:
                self.adicionar(add,worksheet)
                return False
            else:
                self.worksheet.update(f'A{y}', [add])
                return True

    def delete(self,se,worksheet=None):
        self.restaurar(se)
        antigo = se.pk
        add, worksheet = addicionar(se)
        x = 1
        y = None
        if worksheet == None:
            pks = self.worksheet.col_values(1)
        else:
            worksheet = self.sh.worksheet(worksheet)
            pks = worksheet.col_values(1)
        for i in pks:
            if int(i) == int(antigo):
                y = x
            x += 1
        if y == None:
            return False
        else:
            self.worksheet.delete_row(y)
            return True

    def add(self, se):
        salvar = None
        if se.pk:
            salvar = 1
        else:
            salvar = 0
        self.salvar = salvar

    def enviar(self, se):
        self.restaurar(se)
        if self.salvar == 1:
            self.updata(se)
        elif self.salvar == 0:
            self.adicionar(se)


    def restaurar(self, se):
        add, worksheet = addicionar(se)
        serializers.deserialize("json", self.lertabmod(worksheet), ignorenonexistent=True)

google_sheets = Sheets()
