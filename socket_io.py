import time

import redis
from emitter import Emitter


def main():
    io = Emitter({
        'client': redis.StrictRedis()
    })

    while True:
        time.sleep(0.1)

        io.In('group_471f171a-5552-4a70-b5c9-e942cd4fcaf3').Emit(
            'comment',
            {
                'user': {
                    'id': 1
                },
                'comment': {
                    'message': 'test'
                }
            }
        )


if __name__ == '__main__':
    main()
