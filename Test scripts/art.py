from ascii_magic import AsciiArt, from_image
import os

path = os.getcwd()+("\\wvrine.jpg")
print(path)
print("\n"*2)
# This:
my_art = AsciiArt.from_image(path)
my_art.to_terminal()

print("\n"*2)

# Does the same as this:
#my_art = from_image('lion.jpg')
#my_art.to_terminal()