import sys

import sysv_ipc


def receive_message(queue):
  mq = sysv_ipc.MessageQueue(queue)
  while True:
    message, _ = mq.receive()
    value = message.decode()
    if value == "exit":
      print("Turn end!")
      break
    if not value:
      break
    print("Received:", value)


def send_message(queue, nb_players):
  objects_dict = {}
  for i in range(nb_players):
    object_name = f"object_{i}"
    objects_dict[object_name] = sysv_ipc.MessageQueue(queue,
                                                      sysv_ipc.IPC_CREAT)

  while True:
    try:
      value = str(input("Enter a message (Enter exit to exit): "))
    except EOFError:
      break
    except Exception as e:
      print("Input error:", e)
      continue

    if value == "exit":
      message = str(value).encode()
      for name, obj in objects_dict.items():
        obj.send(message)
      break

    message = str(value).encode()
    for name, obj in objects_dict.items():
      obj.send(message)


#turn == 1 : give hint


def chat_process(queue, turn, nb_players):
  if turn == 1:
    send_message(queue, nb_players)
  else:
    receive_message(queue)


if __name__ == "__main__":
  queue_id = 128
  chat_process(queue_id, int(sys.argv[1]), int(sys.argv[2]))
