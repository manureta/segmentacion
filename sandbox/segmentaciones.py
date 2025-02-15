# -*- coding: utf-8 -*-
"""
título: arbol_segmentaciones.py
descripción: calcula los segmentos posibles siguiendo adyacencias
para el caso de conteos o listados con manzanas con pocas viviendas
que se pasan a conteos para evitar segmentos que contengan 
listado parcial y una o más manzanas completas 
usando classes
fecha: 2019-07-13
autor: -h
"""
from operator import *

segmentacion_deseada = 40

class Procesando:
        
    def __init__(self):
        self.reloj = '-'

    def proximo(self):
        if self.reloj == '-':
            self.reloj = '\\'
        elif self.reloj == '\\':
            self.reloj = '|'
        elif self.reloj == '|':
            self.reloj = '/'
        elif self.reloj == '/':
            self.reloj = '-'
        return self.reloj

def set_segmentacion_deseada(valor):
    global segmentacion_deseada
    segmentacion_deseada = int(valor)

class Componente:
    # elemento unitario o indivisible para el caso de segmentación
    # puede ser un lado o una manzana

    def __init__(self, id, vivs):
        self.adyacentes = []
        self.id = id
        self.vivs = vivs

    def __str__(self):
        return str((self.id, self.vivs))

    def agregar_adyacencia(self, ady):
        self.adyacentes.append(ady)

class Componentes(list):

    def __str__(self):
        s = ''
        for c in self:
            s += str(c) + ' '
        return s

    def ids(self):
        return [c.id for c in self]

    def min_id(self):
        return min(self.ids())

    def segmentos(self):
        sgms = Segmentos()
        for c in self:
            sgms.append(Segmento([c]))
        cantidad = 0
        while cantidad < len(sgms):
        # no se incrementó la cantidad de segmentos
            cantidad = len(sgms)
            for s in sgms:
                for c in s:
                    for c_i in c.adyacentes:
                        if c_i in self and c_i not in s:
                            s_mas_c_i = Segmento(s)
                            s_mas_c_i.append(c_i)
                            s_mas_c_i.ordenar()
                            if s_mas_c_i not in sgms:
                                sgms.append(s_mas_c_i)
        return sgms

    def ordenar(self):
        self.sort(key=lambda x: x.id)
        return

    def recorridos(self, 
        hasta=max(1.5*segmentacion_deseada, segmentacion_deseada + 4),
        desde=min(0.5*segmentacion_deseada, segmentacion_deseada - 4)):
        sgms = Segmentos()
        for c in self:
            sgms.append(Segmento([c]))
        cantidad = 0
        while cantidad < len(sgms):
            cantidad = len(sgms)
            for s in sgms:
                ultimo = s[-1] # con el último arma recorridos
                for c in ultimo.adyacentes:
                    if (c in self and c not in s
                        and c.vivs + s.costo() < hasta):
                        s_mas_c = Segmento(s)
                        s_mas_c.append(c)
                        if s_mas_c not in sgms:
                            sgms.append(s_mas_c)
        for s in sgms:
            if s.costo()<desde:
                sgms.remove(s)
            return Segmentos(sgms)

    def componentes(self):
        # devuelve los componentes ordenados
        return self

    def manzanas(self):
        return len(list(set([c.id/10 for c in self.componentes()])))

    def mejor_costo_teorico(self):
        return (1.1*abs(mod(sum(c.vivs for c in self) - (segmentacion_deseada/2),
                        segmentacion_deseada) 
                    - (segmentacion_deseada/2)
                    )
                + 0.01*self.manzanas()) 


class Segmento(Componentes):

    def carga(self):
        return sum(c.vivs for c in self) - segmentacion_deseada 

    def costo(self):
        return abs(self.carga())

    def __str__(self):
        s = '['
        for c in self:
            s += str(c.id) + ' '
        s += '] ' + str(self.carga())
        return s

    def componentes(self):
        # devuelve su lista de componentes
        return Componentes(super().componentes())

    def id(self):
        return self.min_id()

    def ordenado(self):
        # devuelve una copia del segmento con sus componentes ordenados por id
        copia = Segmento(self)
        copia.sort(key=lambda x: x.id)
        return copia

    def equivalente(self, otro):
        # devuelve verdadero si tiene los mismos componentes
        return set(self.componentes()) == set(otro.componentes())

class Segmentos(list):

    def __str__(self):
        s = '['
        for sgm in self:
            s += ' ' + str(sgm) + ' '
        s += ('] Costo: ' + str(self.costo()) 
            + ' (Min: ' + str(self.min_carga()) 
            + ' Max: ' + str(self.max_carga()) + ')')
        return s

    def suma_de_costos_de_segmentos(self):
        return sum(sgm.costo() for sgm in self)

    def maxima_diferencia_de_costos_entre_segmentos(self):
        return self.max_carga() - self.min_carga()

    def suma_cantidad_de_mzas_x_sgm(self):
        return sum(s.manzanas() for s in self)

    def costo(self):
        return (self.suma_de_costos_de_segmentos()
                + 0.1*(self.maxima_diferencia_de_costos_entre_segmentos())
                + 0.01*self.suma_cantidad_de_mzas_x_sgm())

    def max_carga(self):
        return max(sgm.carga() for sgm in self)

    def min_carga(self):
        return min(sgm.carga() for sgm in self)

    def ordenar(self):
        # ordena el conjunto de segmentos segun sus costos y lo devuelve
        self.sort(key=lambda x: x.costo())
        return self

    def componentes(self):
        # devuelve la lista de componentes del conjunto de segmentos
        return [c for s in self for c in s.componentes()]

    def equivalentes(self, otros):
        # para unificar circuitos
        # define equivalencia entre conjunto de segmentos
        # 1. tienen la misma cantidad de elementos
        # 2. las secuencias ordenadas de segmentos 
        # de self y otros son equivalentes uno a uno
        if len(self) != len(otros):
            return False
        self.sort(key=lambda x: x.min_id())
        otros.sort(key=lambda x: x.min_id())
        for i, s in enumerate(self):
            if (not s.equivalente(otros[i])):
                return False
        return True

class Segmentacion(Segmentos):

    def ordenada(self):
        # devuelve una copia con los segmentos ordenada por min_id
        ordenada = Segmentacion(self)
        ordenada.sort(key=lambda s: s.min_id())
        return ordenada

    def canonica(self):
        # devuelve una forma unica de representar segmentacion
        # con los segmentos ordenados por min_id
        # y los componentes ordenados por id dentro de cada segmento
        una = Segmentacion()
        for sgm in self:
            s = sgm.ordenado()
            una.append(s)
        return una.ordenada()

    def equivalente(self, otra):
        return super().equivalentes(otra)

class Segmentaciones(list):

    def diferentes(self):
        # devuelve las segmentaciones que tienen una única
        # representación canónica
        lista = Segmentaciones()
        for i, s_i in enumerate(self):
            esta = False
            for s_j in lista:
                if s_i.equivalentes(s_j):
                    esta = True
            if not esta:
                lista.append(s_i)    
        return lista

    def ultima(self):
        if self:
            return self[-1]
        return None
                  
reloj = Procesando()

def segmenta(segmentacion, componentes, soluciones):
    if componentes == Componentes():
        if (soluciones == Segmentaciones()
            # no encontró soluciones aún, segmentación es la primera
            or segmentacion.costo() == soluciones.ultima().costo()
            # el costo de la segmentacion es igual al de la ultima
                and segmentacion.canonica() not in soluciones.diferentes()):
                # y no está entre las soluciones diferentes (en el grupo de equivalentes)
            #print(len(soluciones),end='',flush=True)
            print('\b'*(len(str(len(soluciones) - 2)) + 2) + str(len(soluciones)) + ' ',end='',flush=True)
            soluciones.append(segmentacion.canonica())
        elif segmentacion.costo() < soluciones.ultima().costo():
            # mejora el costo
            print("\nSol ant: " 
                + str(soluciones.ultima().costo())
                + " Mejor: " + str(segmentacion.costo()))
            print(segmentacion.canonica())
            soluciones[:]=Segmentaciones([segmentacion.canonica()])
        return

    else:
        if (soluciones == Segmentaciones() 
            or segmentacion.costo() + componentes.mejor_costo_teorico() 
                <= soluciones.ultima().costo()):
            sgms = componentes.recorridos(44,36)
            sgms.ordenar()
            for s in sgms:
                segmts = Segmentacion(segmentacion)
                segmts.append(s)
                nueva = segmts
                resto = Componentes(set(componentes) - set(nueva.componentes()))
                if (soluciones == [] 
                    or nueva.costo() + resto.mejor_costo_teorico() 
                        <= soluciones.ultima().costo()):
                    print("\b\b" + ' ' + reloj.proximo(),end='', flush=True)
                    segmenta(nueva, resto, soluciones)
