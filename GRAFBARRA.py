
#Bibliotecas utilizadas
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np

trON =pd.read_csv("TRANS_ON.csv", sep=";") 
trOFF =pd.read_csv("TRANS_OF.csv", sep=";")

# %%
#Mudar o tipo da coluna setor para string para poder fazer o join
trON["SETOR"]=trON["SETOR"].astype("str")
trOFF["SETOR"]=trOFF["SETOR"].astype("str")

#Criando um dataframe com informações dos dois bd
df = trON.append(trOFF, sort=False)

# %%
#Excluindo colunas desnecessarias

#df
df=df.drop("BaselineID",axis=1)
df=df.drop("Group",axis=1)
df=df.drop("TransOrder",axis=1)
df=df.drop("ProcTime",axis=1)
df=df.drop("StartX",axis=1)
df=df.drop("StartY",axis=1)
df=df.drop("EndX",axis=1)
df=df.drop("EndY",axis=1)
df=df.drop("Azimuth",axis=1)
df=df.drop("Autogen", axis=1)
df=df.drop("OBJECTID",axis=1)

# %%
#Renomear colunas
df.rename(columns={'SHAPE_Leng': 'DISTANCIA'}, inplace=True)

# %%
#Verificar o tipo das colunas

#Preciso trocar de "," para "." porque o pandas é americano
df["DISTANCIA"]=df["DISTANCIA"].apply(lambda x: str(x).replace(",","."))

#Mudando de object para float64
df["DISTANCIA"]=df["DISTANCIA"].astype("float64")


# %%
#Criando as colunas do ano anterior e do ano atual

def colunaAno(ano):
    periodo=[]
    for j in range(len(df)):
        periodo.append(ano)
    return periodo

#ano inicial
anoInicial=colunaAno(2017)
#ano final
anoFinal=colunaAno(2020)

#inserindo as colunas no banco de dados
qtdColunasDF=df.shape[1]

def inserirColunasDF(df,variavel,descricaoVariavel):
    qtdColunasDF=df.shape[1]
    df.insert(loc=qtdColunasDF,column=descricaoVariavel,value=variavel)
    return df
inserirColunasDF(df,anoInicial,"ANO INICIAL")
inserirColunasDF(df,anoInicial,"ANO FINAL")

# %%
#Fazendo filtro
#Resumo do dataframe
resumoDF = df['SETOR'].value_counts().to_dict()

# %%
#Criar o data frame resumindo os dados dos setores

#Criando as colunas do dataframe

#Setor (S)
#• Período (P)
#• Quantidade de transectos (T)
#• Distância mínima (DMIN)
#• Distância máxima (DMAX)
#• Média aritmética (MA)
#• Desvio Padrão (DP)
#• Taxa média de variação (TX M)

#Setores
s=[]
for c in resumoDF:
    s.append(c[0])
s=sorted(s)
print(type(s))
print(len(s))

#Classificação do setor

def classificaoSetor(txMSetor):
    if txMSetor<-2:
        return "Erosão Muito Alta"
    elif txMSetor<-1 and txMSetor>=-2:
        return "Erosão Alta"
    elif txMSetor<-1 and txMSetor>0:
        return "Erosão Moderada"
    elif txMSetor==0:
        return "Estável"
    elif txMSetor<0 and txMSetor>=1:
        return "Acreção Moderada"
    elif txMSetor<1 and txMSetor>=2:
        return "Acreção Alta"
    else:
        return "Acreção Muito Alta"
#Estatísticas descritivas
t=[]
dMin=[]
dMax=[]
mA=[]
p=[]
cS=[]
setores=[]
txM=[]

for i in range(1,len(s)+1):
    setori=(df[df["SETOR"]==str(i)])
    print
    setores.append(str(i))

    #Quantidade de transectos
    t.append(len(setori)) 
    #Distância mínima (DMIN)
    dMin.append(setori["DISTANCIA"].min())
    #Distância máxima (DMAX)
    dMax.append(setori["DISTANCIA"].max())
    #Média aritmética (MA)
    mA.append(setori["DISTANCIA"].mean())
    #Taxa media nova
    txM.append(((setori["DISTANCIA"].sum())/(anoFinal[0]-anoInicial[0]))/t[i-1])
    #Periodo (MA)
    p.append(str(anoInicial[0]) + "-" + str(anoFinal[0]))
    #Classificação do Setor (CS)
    cS.append(classificaoSetor(txM[i-1]))

tabelaCompleta =pd.DataFrame(setores,columns=["SETORES"])

inserirColunasDF(tabelaCompleta,t,"QTD TRANSECTOS")
inserirColunasDF(tabelaCompleta,dMin,"DMIN")
inserirColunasDF(tabelaCompleta,dMax,"DMAX")
inserirColunasDF(tabelaCompleta,mA,"MÉDIA")
inserirColunasDF(tabelaCompleta,txM,"TX VARIAÇÃO")
inserirColunasDF(tabelaCompleta,cS,"CLASSIFICAÇÃO")
inserirColunasDF(tabelaCompleta,p,"PERÍODO")

# %%
#Exportando a tabela para o formato latex

import matplotlib.pyplot as plt
print(tabelaCompleta.to_latex(index = True, multirow = True))

# %%
labels=cS

# %%
#Gráfico de barra

import matplotlib.pyplot as plt

#Fazendo o titulo
titulo="Taxa Média de Variação (" + str(anoInicial[0]) + " - " + str(anoFinal[0]) + ")"
#titulo="Gráfico de Barras"
eixox="Setores"
eixoy="Taxa Média (m/ano)"

#Legendas
plt.title(titulo)
plt.xlabel(eixox)
plt.ylabel(eixoy)

#Cores
def coresSetoresRGB(taxaVariacao):
    coresRGB=[]
    for i in range(len(taxaVariacao)):
        if taxaVariacao[i]<0:
            coresRGB.append("#4CE600")
        elif taxaVariacao[i]>0:
            coresRGB.append("#E64C00")
        else: 
            coresRGB.append("gray")
    return coresRGB

def situacaoSetores(taxaVariacao):     
    situacao=[]
    for i in range(len(taxaVariacao)):
        if txM[i]<0:
            situacao.append("Erosão")
        elif txM[i]>0:
            situacao.append("Acreção")
        else: 
            situacao.append("Estabilidade")
    return situacao

colors=dict(zip(situacaoSetores(txM), coresSetoresRGB(txM)))

#gráfico
plt.bar(s,txM,color=(coresSetoresRGB(txM)))

#Legenda
labels = list(colors.keys())
handles = [plt.Rectangle((1,-12),5,-12, color=colors[label]) for label in labels]
plt.legend(handles, labels,loc=4)

#salvando como figura
plt.savefig("grafico de barra.pdf")

# %%
#Exportando para csv
tabelaCompleta.to_csv("resumoSetores.csv")

#########
coroa=gpd.read_file("SETORES_2017_2020.shp")

df =pd.read_csv("resumoSetores.csv", sep=",")

#Renomear coluna
df.rename(columns={'SETOR': 'SETORES'}, inplace=True)

#MERGE
coroa2020 = coroa.merge(df, on='SETORES')

#inserindo lc 2020
lc2020=gpd.read_file("LC_GNSS_2020_POL_UTM.shp") #inseriondo linha de costa de 

#inserindo lc 2017
lc2017=gpd.read_file("LC_GNSS_2017_POL_UTM.shp")

#Mudar a cor das linhas
coresMapa=coresSetoresRGB(coroa2020["TX VARIAÇÃO"])

#Para unir todos os shapes
fig, ax=plt.subplots(1) 
lc2020.plot(ax=ax, color="#191970")
lc2017.plot(ax=ax, color="#0000CD")
coroa2020.plot(ax=ax,column="CLASSIFICAÇÃO",color=coresMapa)

#Layout
corCoroa2020 = {"LC " + str(anoFinal[0]):"#191970","LC " + str(anoInicial[0]):"#0000CD" }
corCoroa2020.update(colors)
ax.set_facecolor('#c9f4fe')#mar
labels = list(corCoroa2020.keys())
plt.title(titulo)
handles = [plt.Rectangle((1,-12),5,-12, color=corCoroa2020[label]) for label in labels]
plt.legend(handles, labels,loc=4)
plt.show()
