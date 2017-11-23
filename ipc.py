from fs import fs

IPC_KEY_SIZE = 4


def get_ipc_key(superblock):
    s_uuid = superblock.get_field(superblock.s_uuid)

    key = 0
    for i in range(len(s_uuid) // IPC_KEY_SIZE):
        key ^= fs.bytes_to_int(s_uuid[i * IPC_KEY_SIZE: (i+1) * IPC_KEY_SIZE])
    return key
