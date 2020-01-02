from network import Network

network = Network()
network.sendrecv('command')

while True:
    print('> ', end='')
    command = input()
    if command == 'exit':
        break
    network.sendrecv(command)

    
network.sendrecv('land')
network.close()
