lista = ["4o","4o-mini", "o1-prewiew", "o1- mini"]

# c style NON USARE 
for i in range(0,len(lista)):
    print("chatGPT " + lista[i])
       
# py style

for versione in lista:
    print(f"chatGPT {versione}")
    
# enumerate

for num, versione in enumerate(lista):
    print(f"{num + 1}° versione di chatGPT: {versione}")
    
nomi = ["herman", "poggis", "mauro", "sbruma"]

for nome,versione in zip(nomi,lista):
    print(f"{nome} usa chatGPT {versione}")
    
nomi.append("cioffi")
print(nomi[-2:])