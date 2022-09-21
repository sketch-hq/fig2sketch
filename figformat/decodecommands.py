import struct

# M2.64274e-19 18.7108
# C2.64274e-19 15.9636 1.12696 13.3327 3.34683 11.7142
# C9.06624 7.5442 21.7915 0 39 0
# C56.2085 0 68.9338 7.5442 74.6532 11.7142
# C76.873 13.3327 78 15.9636 78 18.7108
# L78 71.4072
# C78 76.9301 73.5229 81.4072 68 81.4072
# L10 81.4072
# C4.47715 81.4072 2.64274e-19 76.9301 2.64274e-19 71.4072
# L2.64274e-19 18.7108
# Z",
commands = b'\x01\x00\x00\x9c \xc0\xaf\x95A\x04\x00\x00\x9c \xc8j\x7fAP@\x90?\xaeRUA\x852V@Qm;A\x04T\x0f\x11A\x0fj\xf1@\x15U\xaeA\x00\x00\x00\x00\x00\x00\x1cB\x00\x00\x00\x00\x04v\xd5`B\x00\x00\x00\x00\x16\xde\x89B\x11j\xf1@lN\x95BRm;A\x04\xff\xbe\x99B\xafRUA\x00\x00\x9cB\xc8j\x7fA\x00\x00\x9cB\xc0\xaf\x95A\x02\x00\x00\x9cB\x82\xd0\x8eB\x04\x00\x00\x9cB5\xdc\x99B\xb3\x0b\x93B\x82\xd0\xa2B\x00\x00\x88B\x82\xd0\xa2B\x02\xff\xff\x1fA\x82\xd0\xa2B\x04\xd4D\x8f@\x82\xd0\xa2B\x00\x00\x9c 5\xdc\x99B\x00\x00\x9c \x82\xd0\x8eB\x02\x00\x00\x9c \xc0\xaf\x95A\x00'

COMMANDS = {
    1: ('M', 2),
    4: ('C', 6),
    2: ('L', 2),
    0: ('Z', 0),
}

i = 0
while i < len(commands):
    command, num_params = COMMANDS[int(commands[i])]
    i += 1
    params = []
    for p in range(num_params):
        params.append(struct.unpack('<f', commands[i:i+4])[0])
        i += 4
    print(command, params)
