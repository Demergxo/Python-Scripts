

message = "Three can keep a secret, if two of them are dead."
translated = ""
i = len(message) - 1

while i >= 0:
    translated = translated + message[i]
    i -= 1

print(translated)

message = input("Enter a message: ")
translated = ""
i = len(message) - 1

while i >= 0:
    translated = translated + message[i]
    i -= 1

print(translated)

print(len("Hello")+len("Hello"))

i= 0
spam = "Hello"
while i < 5:
    spam = spam + spam[i]
    i += 1
print(spam)

i=0
while i<4:
    while i<3:
        i=i+2
        print(i)
    
    
