import tkinter as tk
from tkinter import scrolledtext, messagebox
import ply.lex as lex
import ply.yacc as yacc
import graphviz
import os
from graphviz import Digraph

# Tabla de símbolos con IDs
tabla_simbolos = {}
codigo_intermedio = []  # Almacena el código intermedio
transiciones = {}  # Almacena transiciones para el DFA
token_count = 0  # Contador de tokens para nombrar estados

# Definimos los tokens
tokens = (
    'IDENTIFICADOR', 'NUMERO', 'SUMA', 'RESTA', 'MULTIPLICA', 'DIVIDE',
    'PARENTESIS_IZQ', 'PARENTESIS_DER', 'IGUAL', 'PUNTOYCOMA', 'COMA', 'CARACTER',
    'IF', 'FOR', 'INT', 'STRING', 'CHAR'
)

t_SUMA = r'\+'
t_RESTA = r'-'
t_MULTIPLICA = r'\*'
t_DIVIDE = r'/'
t_IGUAL = r'='
t_PARENTESIS_IZQ = r'\('
t_PARENTESIS_DER = r'\)'
t_PUNTOYCOMA = r';'
t_COMA = r','

def t_IF(t):
    r'if'
    return t

def t_FOR(t):
    r'for'
    return t

def t_INT(t):
    r'int'
    return t

def t_STRING(t):
    r'string'
    return t

def t_CHAR(t):
    r'char'
    return t

def t_CARACTER(t):
    r'\'[^\']*\''
    return t

def t_IDENTIFICADOR(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    return t

def t_NUMERO(t):
    r'\d+'
    t.value = int(t.value)
    return t

t_ignore = ' \t\n'

def t_error(t):
    print(f"Carácter no reconocido: {t.value[0]}")
    t.lexer.skip(1)

analizador_lexico = lex.lex()

# Precedencia de operadores
precedence = (
    ('left', 'SUMA', 'RESTA'),    
    ('left', 'MULTIPLICA', 'DIVIDE')  
)

# Definimos la gramática
def p_declaracion_multiple(p):
    'declaracion : asignaciones PUNTOYCOMA'
    p[0] = p[1]

def p_asignaciones_lista(p):
    'asignaciones : asignaciones COMA asignacion'
    p[0] = p[1] + [p[3]]

def p_asignaciones_unica(p):
    'asignaciones : asignacion'
    p[0] = [p[1]]

def p_asignacion(p):
    'asignacion : tipo IDENTIFICADOR IGUAL expresion'
    tipo = p[1]
    identificador = p[2]
    valor = p[4]
    
    if identificador in tabla_simbolos:
        print(f"Error semántico: Variable '{identificador}' ya declarada")
    else:
        tabla_simbolos[identificador] = (tipo, valor)
    
    temp_var = f"t{len(codigo_intermedio)}"
    codigo_intermedio.append(f"{temp_var} = {valor}")
    p[0] = ('asignacion', identificador, valor)

def p_tipo(p):
    '''tipo : INT
            | STRING
            | CHAR'''
    p[0] = p[1]

def p_expresion_operacion(p):
    '''expresion : expresion SUMA expresion
                 | expresion RESTA expresion
                 | expresion MULTIPLICA expresion
                 | expresion DIVIDE expresion'''
    temp_var = f"t{len(codigo_intermedio)}"
    codigo_intermedio.append(f"{temp_var} = {p[1]} {p[2]} {p[3]}")
    p[0] = temp_var

def p_expresion_numero(p):
    'expresion : NUMERO'
    p[0] = p[1]

def p_expresion_identificador(p):
    'expresion : IDENTIFICADOR'
    if p[1] in tabla_simbolos:
        p[0] = tabla_simbolos[p[1]][1]
    else:
        print(f"Error semántico: Variable '{p[1]}' no declarada")

def p_error(p):
    print(f"Error de sintaxis cerca de '{p.value}'" if p else "Error de sintaxis")

analizador_sintactico = yacc.yacc()

def generar_dfa():
    dfa = Digraph(format='png')
    dfa.attr(rankdir='LR')  
    
    estados = set()
    for (origen, simbolo), destino in transiciones.items():
        estados.add(origen)
        estados.add(destino)
    
    for estado in estados:
        dfa.node(estado, shape='circle')
    
    dfa.node('', shape='none')
    dfa.edge('', 'q0')  
    
    for (origen, simbolo), destino in transiciones.items():
        dfa.edge(origen, destino, label=str(simbolo))
    
    dfa.render('dfa_output', format='png', cleanup=True)
    os.system("start dfa_output.png")
    print("DFA generado como 'dfa_output.png'")
    
def dibujar_arbol_sintaxis(arbol, nombre="arbol_sintactico"):
    grafo = graphviz.Digraph()
    def agregar_nodos_y_conexiones(nodo, padre=None):
        if isinstance(nodo, tuple):
            nodo_id = str(id(nodo))
            grafo.node(nodo_id, label=str(nodo[0]))
            if padre:
                grafo.edge(padre, nodo_id)
            for hijo in nodo[1:]:
                agregar_nodos_y_conexiones(hijo, nodo_id)
        else:
            nodo_id = str(id(nodo))
            grafo.node(nodo_id, label=str(nodo))
            if padre:
                grafo.edge(padre, nodo_id)
    agregar_nodos_y_conexiones(arbol)
    grafo.render(nombre, format="png", cleanup=True)
    os.system(f"start {nombre}.png")    

def generar_codigo_tres_direcciones():
    codigo = "\n".join(codigo_intermedio)
    return codigo

class CompilerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Compilador Python")
        self.geometry("800x600")

        self.text_area = scrolledtext.ScrolledText(self, width=80, height=10)
        self.text_area.pack(pady=10)

        self.btn_lexico = tk.Button(self, text="Análisis Léxico", command=self.analisis_lexico)
        self.btn_lexico.pack()

        self.btn_sintactico = tk.Button(self, text="Análisis Sintáctico", command=self.analisis_sintactico)
        self.btn_sintactico.pack()

        self.btn_semantico = tk.Button(self, text="Análisis Semántico", command=self.analisis_semantico)
        self.btn_semantico.pack()

        self.btn_tac = tk.Button(self, text="Código de Tres Direcciones", command=self.mostrar_codigo_tac)
        self.btn_tac.pack()

        self.btn_tabla_simbolos = tk.Button(self, text="Tabla de Símbolos", command=self.mostrar_tabla_simbolos)
        self.btn_tabla_simbolos.pack()

        self.output_area = scrolledtext.ScrolledText(self, width=80, height=10, state='disabled')
        self.output_area.pack(pady=10)

    def analisis_lexico(self):
        codigo = self.text_area.get("1.0", tk.END).strip()
        analizador_lexico.input(codigo)
        tokens = [f"<{tok.type}, {tok.value}>" for tok in analizador_lexico]
        self.mostrar_resultado("Tokens:\n" + "\n".join(tokens))

    def analisis_sintactico(self):
        global tabla_simbolos
        tabla_simbolos.clear()
        codigo = self.text_area.get("1.0", tk.END).strip()
        try:
            resultado = analizador_sintactico.parse(codigo)
            if resultado:
                self.mostrar_resultado(f"Árbol de sintaxis:\n{resultado}")
                dibujar_arbol_sintaxis(resultado)
            else:
                self.mostrar_resultado("Error de sintaxis")
        except Exception as e:
            self.mostrar_resultado(f"Error: {str(e)}")

    def mostrar_tabla_simbolos(self):
        if not tabla_simbolos:
            self.mostrar_resultado("Tabla de Símbolos vacía")
        else:
            tabla_texto = "Tabla de Símbolos:\nID    Tipo    Valor\n" + "\n".join([f"{id}     {tipo}     {valor}" for id, (tipo, valor) in tabla_simbolos.items()])
            self.mostrar_resultado(tabla_texto)


    def mostrar_codigo_tac(self):
        codigo = generar_codigo_tres_direcciones()
        self.mostrar_resultado("Código de Tres Direcciones:\n" + codigo)

    def analisis_semantico(self):
        self.mostrar_resultado("Análisis semántico completado")

    def mostrar_resultado(self, texto):
        self.output_area.config(state='normal')
        self.output_area.delete("1.0", tk.END)
        self.output_area.insert(tk.END, texto)
        self.output_area.config(state='disabled')

if __name__ == "__main__":
    app = CompilerApp()
    app.mainloop()

