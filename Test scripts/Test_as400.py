from p5250 import P5250Client

my_client = P5250Client(hostName='localhost', path='c:\\wc3270\\', codePage='cp277')

# Connect and test if connection succeeded or not
if not my_client.connect():
    print('Connection failed !')
    exit(1)

# Save the home screen to a file called 'home.html'. HTML format is the default.
my_client.saveScreen(fileName='home.html')

# Send user name to the current field (user ID)
my_client.sendText('user1')

# Send TAB key to go to the next field
my_client.sendTab()

# Send the user password to the password field.
my_client.sendText('password1')

# Send Enter key to submit the current screen with field contents
my_client.sendEnter()

# Go back : F3 key
my_client.sendF(3)

# Go back again
my_client.sendF(3)

# Disconnect from the host 
my_client.disconnect()

# End the emulation session
my_client.endSession()