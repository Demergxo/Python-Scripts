rack = "R"
letras = ["A", "B", "C"]
lines = []
alturas =["00", "01"]

for i in range(1,12):
    for j in range(1,53):
        for letra in letras:
            for altura in alturas:
                print("{}{}.{}{}{}".format(rack, str(i).zfill(2), str(j).zfill(3),altura, letra))
                line = "{}{}.{}{}{}".format(rack, str(i).zfill(2), str(j).zfill(3),altura, letra)
                lines.append(line)
with open("fichero.txt", "w")as file:
    for line in lines:
        file.write(line+"\n")
                