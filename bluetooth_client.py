# from mido import MidiFile

# mid = MidiFile('music.mid')

# for i, track in enumerate(mid.tracks):
#     print('Track {}: {}'.format(i, track.name))
#     for msg in track:
#         print(msg)

import socket
# simple inquiry example
import bluetooth

nearby_devices = bluetooth.discover_devices(lookup_names=True)
print("Found {} devices.".format(len(nearby_devices)))

for addr, name in nearby_devices:
    print(addr, name)
    print("  {} - {}".format(addr, name))

client = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
client.connect((addr, 1))

try:
    while True:
        message = input("Enter message:")
        client.send(message.encode("utf-8"))
        #  data = client.recv(1024)
        #  if not data:
        #      break
        #  print(f"Message: {data.decode('utf-8')}")
except OSError as e:
     pass

client.close()

