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
        objects_dict[object_name] = sysv_ipc.MessageQueue(
            queue, sysv_ipc.IPC_CREAT)

    while True:
        try:

            while True:
                name_players = input(
                    "Give information for (1:player 1, 2: player 2): ")
                try:
                    if int(name_players) <= nb_players and int(
                            name_players) > 0:
                        break
                    else:
                        print("Please enter a valid number")

                except Exception as e:
                    print("Please enter a correct number!")
                    continue

            while True:
                color_number = input(
                    "Please give a color or a number of cards: ")
                try:
                    if color_number in [
                            "1", "2", "3", "4", "5", "blue", "red", "green",
                            "purple", "orange", "yellow", "white", "black"
                    ]:
                        break
                    else:
                        print("Please enter a valid color or number")

                except Exception as e:
                    print("Please enter a correct number!")
                    continue

            while True:
                nb = input("How many cards are the same color or number: ")
                try:
                    if int(nb) < 5 and int(nb) > 0:
                        break
                    else:
                        print("Please enter a valid number")

                except Exception as e:
                    print("Please enter a correct number!")
                    continue
            value = "Player " + str(name_players) + " has " + str(
                nb) + " " + str(color_number) + " cards"

            # value = str(input("Enter a message (Enter exit to exit): "))
        except EOFError:
            break
        except Exception as e:
            print("Input error:", e)
            continue

        # if value == "exit":
        #   message = str(value).encode()
        #   for name, obj in objects_dict.items():
        #     obj.send(message)
        #   break

        message = str(value).encode()
        for name, obj in objects_dict.items():
            obj.send(message)

        message = "exit".encode()
        for name, obj in objects_dict.items():
            obj.send(message)

        break


#turn == 1 : give information, other: listen


def chat_process(queue, turn, nb_players):
    if turn == 1:
        send_message(queue, nb_players)
    else:
        receive_message(queue)


if __name__ == "__main__":
    queue_id = 128
    chat_process(queue_id, int(sys.argv[1]), int(sys.argv[2]))
