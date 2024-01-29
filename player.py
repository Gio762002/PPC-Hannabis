import chat
import signal_test
import signal

nb_players = 4
nb_turns = 1


def play_card():
  play = ''
  while play not in ['1', '2', '3', '4', '5']:
    play = input("Please chose a card(1-5):")
  if int(play) <= 5 or int(play) >= 1:
    pass
    #commuicate with server


def give_information():
  global nb_players
  chat.chat_process(128, 1, nb_players)


def choose_phase():
  global nb_players
  phase = ''
  while phase not in ['1', '2']:
    phase = input("Plese chose a phase: (1:play a card, 2:give information)")

  if phase == '1':
    play_card()

  elif phase == '2':
    give_information()


def your_turn(numero_player):
  global nb_turns
  global nb_players
  if numero_player == nb_turns:
    choose_phase()
    nb_turns += 1
    if nb_turns > nb_players:
      nb_turns -= nb_players
  else:
    chat.chat_process(128, 0, nb_players)


in_hand = []
signal.signal(signal.SIGUSR1, signal_test.handle_win)
signal.signal(signal.SIGUSR2, signal_test.handle_loss)
your_turn(2)
