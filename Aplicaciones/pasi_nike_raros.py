ubicaciones = ["V","W","X","Y","Z"]
location = []
pasillo = 13



for modulo in range(1,68):
    for ubicacion in ubicaciones:
        for altura in range(0,4):
        
            print("{}.{}{}{}".format(str(pasillo).zfill(2), str(modulo).zfill(3), str(altura).zfill(2), ubicacion))
            loc = "{}.{}{}{}".format(str(pasillo).zfill(2), str(modulo).zfill(3), str(altura).zfill(2), ubicacion)
            location.append(loc)
            
with open("locs_nike.txt", "w") as file:

    for line in location:
        file.write(line+"\n")