from copy import deepcopy


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class ConflictError(Error):

    def __init__(self, message):
        self.message = message


class Productie:
    _neterminal = ""
    _regula = ""
    punctul = 0

    def __init__(self, neterminal, regula):
        super().__init__()
        self._neterminal = neterminal
        self._regula = regula

    def __str__(self) -> str:
        x = self._regula.split(' ')[self.punctul:]
        y = self._regula.split(' ')[:self.punctul]
        return self._neterminal + " -> " + " ".join(y) + "." + " ".join(x)

    def __repr__(self) -> str:
        x = self._regula.split(' ')[self.punctul:]
        y = self._regula.split(' ')[:self.punctul]
        return self._neterminal + " -> " + " ".join(y) + "." + " ".join(x)

    def __eq__(self, o: object) -> bool:
        return self._neterminal == o._neterminal and self._regula == o._regula and self.punctul == o.punctul

    def get_neterminal(self):
        return self._neterminal

    def get_regula(self):
        return self._regula

    def isFinala(self):
        return self.punctul == len(self._regula.split(' '))

    def getSimbol(self):
        if self.isFinala():
            raise Exception("not final")
        return self._regula.split(' ')[self.punctul]

    def __hash__(self) -> int:
        return hash(self._neterminal) + hash(self._regula) + hash(self.punctul)


class Gramatica:
    _neterminale = []
    _terminale = []
    _reguliProductie = []
    _simbolStart = ""

    _simboluri = []

    contor = -1

    _stari = []

    lista_foarte_ineficienta = []

    first = {}

    follow = {}

    def _read(self, filename):
        ok = False
        with open(filename) as file:
            for line in file:
                neterminal, regula = line.split("->")
                neterminal = neterminal.strip()
                regula = regula.strip()
                productie = Productie(neterminal, regula)
                if not ok:
                    self._simbolStart = neterminal
                    ok = True
                self._reguliProductie.append(productie)
                if neterminal not in self._neterminale:
                    self._neterminale.append(neterminal)
                for x in regula.split(' '):
                    if x not in self._terminale:
                        self._terminale.append(x)

        for x in self._neterminale:
            if __name__ == '__main__':
                if x in self._terminale:
                    self._terminale.remove(x)

        self._simboluri = self._terminale + ["$"] + self._neterminale

    def __init__(self, filename):
        super().__init__()
        # aici citesc din fisier
        self._read(filename)

    def print(self):
        print(self._simbolStart)
        print(self._neterminale)
        print(self._terminale)
        print(self._reguliProductie)

    def simbolStart(self):
        return self._simbolStart

    def neterminale(self):
        return self._neterminale

    def terminale(self):
        return self._terminale

    def reguliProductie(self):
        return self._reguliProductie

    def inclass(self):
        print("Reguli de productie recursive la dreapta:")
        for productie in self._reguliProductie:
            if productie.get_regula().endswith(productie.get_neterminal()):
                print(productie)

    def addSLRTable(self):
        self._reguliProductie.append(Productie("S'", self._simbolStart))
        initiale = [self._reguliProductie[-1]]
        self.add(initiale)

    def allFirst(self):
        # compute first for every non terminal
        self.first = {x: [] for x in self._neterminale}
        for x in self._neterminale:
            self.firstF(x)

    def firstF(self, neterminal):
        if self.first[neterminal]:
            return
        m = self.lab5_1(neterminal)
        for prod in m:
            regula = deepcopy(prod.get_regula().split(' '))
            self.r(neterminal, regula)

    def r(self, neterminal, regula):
        x = regula[0]
        if x in self._neterminale:
            if x == neterminal:
                return
            if not self.first[x]:
                self.firstF(x)
            for a in self.first[x]:
                if a == "eps":
                    self.r(neterminal, deepcopy(regula[1:]))
                else:
                    if a not in self.first[neterminal]:
                        self.first[neterminal].append(a)
        else:
            if x not in self.first[neterminal]:
                self.first[neterminal].append(x)

    def followAll(self):
        self.allFirst()
        self.follow = {x: [] for x in self._neterminale}
        self.follow[self._simbolStart].append("$")
        for x in self._neterminale:
            self.followF(x)

    def followF(self, neterminal):
        if neterminal != self._simbolStart and self.follow[neterminal]:
            return
        m = self.ajutor(neterminal)
        for prod in m:
            regula = deepcopy(prod.get_regula().split(' '))
            self.f(neterminal, regula, prod.get_neterminal())

    def f(self, neterminal, regula, x):
        n = len(regula)
        for i in range(n):
            if regula[i] == neterminal:
                if i == n - 1:
                    aux = self.follow[x]
                else:
                    u = regula[i + 1]
                    if u in self._neterminale:
                        aux = self.first[u]
                    else:
                        aux = []
                        if u not in self.follow[neterminal]:
                            self.follow[neterminal].append(u)
                for a in aux:
                    if a == "eps":
                        self.f(neterminal, deepcopy(regula[0:i+1]+regula[i+2:]), x)
                    else:
                        if a not in self.follow[neterminal]:
                            self.follow[neterminal].append(a)

    def add(self, initiale):
        n = len(self.lista_foarte_ineficienta)
        for x in range(n):
            if set(self.lista_foarte_ineficienta[x]) == set(initiale):
                return x
        self.lista_foarte_ineficienta.append(deepcopy(initiale))
        id = len(self.lista_foarte_ineficienta) - 1
        stare = self.o_functie_recursiva(initiale)
        self._stari.append([None]*(len(self._neterminale)+len(self._terminale) + 1))
        d = {}
        for productie in stare:
            if not productie.isFinala():
                ceva = self.goto(productie)
                m = [ceva[0]]
                if ceva[1] in d:
                    continue
                d[ceva[1]] = 1
                for productie2 in stare:
                    if productie != productie2:
                        try:
                            if str(productie2.getSimbol()) == str(ceva[1]):
                                p = deepcopy(productie2)
                                p.punctul += 1
                                m.append(p)
                        except Exception as e:
                            pass
                aux = self.add(m)
                if ceva[1] in self._neterminale:
                    if self._stari[id][self._simboluri.index(ceva[1])] is None:
                        self._stari[id][self._simboluri.index(ceva[1])] = aux
                    else:
                        raise ConflictError("Conflict error")
                else:
                    if self._stari[id][self._simboluri.index(ceva[1])] is None:
                        self._stari[id][self._simboluri.index(ceva[1])] = "s" + str(aux)
                    else:
                        raise ConflictError("Conflict error")
            else:
                iudh = None
                for i in range(len(self._reguliProductie)):
                    if self._reguliProductie[i].get_neterminal() == productie.get_neterminal() and self._reguliProductie[i].get_regula() == productie.get_regula():
                        iudh = i
                if iudh == len(self._reguliProductie)-1:
                    if self._stari[id][len(self._terminale)] is None:
                        self._stari[id][len(self._terminale)] = "accept"
                    else:
                        raise ConflictError("Conflict error")
                else:
                    for i in range(len(self._terminale) + 1):
                        if self._stari[id][i] is None:
                            if self._simboluri[i] in self.follow[productie.get_neterminal()]:
                                self._stari[id][i] = "r"+str(iudh)
                        else:
                            ConflictError("Conflict error")
        return id

    def o_functie_recursiva(self, l):
        lista = deepcopy(l)
        n = len(lista)
        i = 0
        dict = {}
        while i < n:
            try:
                if lista[i].getSimbol() in dict:
                    i += 1
                    continue
            except Exception:
                i += 1
                continue
            aux = self.closure(lista[i])
            lista += aux
            dict[lista[i].getSimbol()] = 1
            i += 1
            n += len(aux)
        return lista

    def closure(self, productie):
        try:
            if productie.getSimbol() in self._neterminale:
                m = self.lab5_1(productie.getSimbol())
                return m
        except Exception:
            pass
        return []

    def goto(self, productie):
        x = productie.getSimbol()
        p = deepcopy(productie)
        p.punctul += 1
        return p, x

    def lab5_1(self, neterminal):
        # multimea tuturor regulilor de productie care au un anumit neterminal in stanga
        m = []
        for productie in self._reguliProductie:
            if productie.get_neterminal() == neterminal:
                m.append(productie)
        return m

    def ajutor(self, neterminal):
        # multimea tuturor regulilor de productie care au un anumit neterminal in dreapta
        m = []
        for productie in self._reguliProductie:
            if neterminal in productie.get_regula().split(' '):
                m.append(productie)
        return m

    def afiseaza(self):
        self.followAll()
        self.addSLRTable()
        # print(self.lista_foarte_ineficienta)
        # print(self._simboluri)
        for a in self._stari:
            print(a)
        # print(self._stari)

    def accepta(self, inp):
        stack = [0]
        cursor = 0
        chestie = []
        while True:
            if inp[cursor] not in self._simboluri:
                print(inp[cursor], "undeclared")
                break
            casuta = self._stari[stack[-1]][self._simboluri.index(inp[cursor])]
            try:
                i = int(casuta)
                stack.append(i)
            except Exception:
                if casuta is None:
                    print("am crapat la:", inp[cursor], cursor)
                    # print("Eroare")
                    break
                elif casuta == "accept":
                    print("Accepted")
                    chestie.reverse()
                    print("Sirul productiilor:", "".join([str(x) for x in chestie]))
                    break
                elif casuta[0] == "s":
                    x = int(casuta[1:])
                    stack.append(inp[cursor])
                    cursor += 1
                    stack.append(x)
                elif casuta[0] == "r":
                    x = int(casuta[1:])
                    chestie.append(x+1)
                    prod = self._reguliProductie[x]
                    i = len(prod.get_regula().split(' '))
                    for j in range(2*i):
                        stack.pop()
                    stack.append(prod.get_neterminal())
                    casuta = self._stari[stack[-2]][self._simboluri.index(prod.get_neterminal())]
                    stack.append(casuta)
                else:
                    print("ce dracu")
                    break

    def eOK(self, secv):
        self.followAll()
        try:
            self.addSLRTable()
            self._reguliProductie = self._reguliProductie[:-1]
            self.accepta(secv + ["$"])
        except ConflictError as e:
            print(e)

    def firstPrint(self):
        self.followAll()
        print("first", self.first)
        print("follow", self.follow)


def citeste_fip():
    secv = []
    with open("FIP.txt") as f:
        for line in f:
            nume, cod = line.split(' ')
            nume = nume.strip()
            cod = cod.strip()
            if cod == '1':
                secv.append("ID")
            elif cod == '2':
                secv.append("CONST")
            else:
                secv.append(nume)
    return secv


def meniu():
    print("\n")
    print("Program de lucru cu gramatici. Comenzile actuale:")
    print("1. Afiseaza simbolul de start al gramaticii")
    print("2. Afiseaza multimea neterminalelor")
    print("3. Afiseaza multimea terminalelor")
    print("4. Afiseaza toate regulile de productie")
    print("5. Afiseaza toate regulile de productie care au in staga un anumit neterminal")
    print("6. Accepta sau refuza secventa")
    print("0. Exit")
    print("-"*40)


def run():
    g = Gramatica("MLP.txt")
    while True:
        meniu()
        cmd = input("> ")
        if cmd == "1":
            print(g.simbolStart())
        elif cmd == "2":
            print(g.neterminale())
        elif cmd == "3":
            print(g.terminale())
        elif cmd == "4":
            print(g.reguliProductie())
        elif cmd == "5":
            neterminal = input("Introduceti neterminalul: ")
            m = g.lab5_1(neterminal)
            if m:
                print(m)
            else:
                print("Nu exista reguli de productie care sa aiba in stanga neterminalul " + neterminal)
        elif cmd == "6":
            # s = input("Introduceti secventa mult dorita: ")
            secv = citeste_fip()
            g.eOK(secv)
        elif cmd == "7":
            g.firstPrint()
        elif cmd == "0":
            break
        else:
            print("Comanda invalida")


if __name__ == '__main__':
    run()
