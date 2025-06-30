class Player:
    def __init__(self, name):  # магический метод, дандер метод
        self.name = name
        self.health = 100
        self.sanity = 100

def play_game():
    print("Ты проснулся в неизвестном тебе месте. Ты не помнишь, кто ты такой, не помнишь, как ты здесь оказался, но ты знаешь одно: нужно поскорее отсюда выбираться.")
    print("Что-ж... Начнём.")

    player_name = input("Введите свое имя: ")
    player = Player(player_name)

    print(f"Ваше здоровье: {player.health}; Ваше психическое состояние: {player.sanity}")

    # раунд 1
    print("Ты видишь что-то ужасное в углу комнаты...")
    choice = input("Что вы хотите сделать?\n1. Убежать из комнаты\n2. Замереть на месте\n3. Подойти ближе к нему\n")
    if choice == "1":
        pass
    elif choice == "2":
        player.health -= 20
        print("Не стоило этого делать")
    elif choice == "3":
        player.health -= 30
        player.sanity -= 50
        print("Это что-то сильно повлияло на ваш разум, вы теряете рассудок")

    print(f"Ваше здоровье: {player.health}; Ваше психическое состояние: {player.sanity}")

    # раунд 2
    print("Здесь так темно… Ты услышал чей-то шёпот")
    choice = input("Что вы хотите сделать?\n1. Закрыть уши\n2. Игнорировать\n3. Громко закричать\n")
    if choice == "1":
        pass
    elif choice == "2":
        player.health -= 20
        player.sanity -= 30
        print(f"Это тебя не спасет, {player.name} - прошептало нечто. Ты постепенно сходишь с ума")
    elif choice == "3":
        player.health -= 50
        player.sanity -= 40
        print("Вам зашили рот, вы больше не сможете кричать")

    print(f"Ваше здоровье: {player.health}; Ваше психическое состояние: {player.sanity}")

    # раунд 3
    print("Ты нашёл жуткую куклу")
    choice = input("Что вы хотите сделать?\n1. Уничтожить\n2. Оставить\n3. Взять с собой\n")
    if choice == "1":
        print(f"Ваше здоровье: {player.health}; Ваше психическое состояние: {player.sanity}")
        pass

    elif choice == "2":
        player.health -= 40
        player.sanity -= 20
        print(f"Она доберётся до тебя, {player.name}")
        print(f"Ваше здоровье: {player.health}; Ваше психическое состояние: {player.sanity}")

    elif choice == "3":
        player.health = 0
        player.sanity = 0
        print("Дух куклы вселился в тебя, ты мёртв")
        return

    if player.health <= 0 or player.sanity <= 0:
        print(f"Стоило хорошенько думать, игрок {player.name}. Игра окончена.")
        return


    # раунд 4
    print("Ты решил выглянуть в окно, но там видна фигура, похожая на призрака")
    choice = input("Что вы хотите сделать?\n1. Занавесить шторы\n2. Посмотреть призраку в глаза\n3. Открыть окно и крикнуть\n")
    if choice == "1":
        print(f"Ваше здоровье: {player.health}; Ваше психическое состояние: {player.sanity}")
        pass
    elif choice == "2":
        player.health = 0
        player.sanity = 0
        print("Оно овладело тобой. Твоя смелость ему не понравилась")
        return
    elif choice == "3":
        if player.sanity <= 0:
            print("Стоило хорошенько думать, игрок {player.name}. Игра окончена.")
            return
        else:
            player.health = 0
            player.sanity = 0
            print("Ты разгневал его, {player.name}. Оно убило тебя")
            return

    if player.health <= 0 or player.sanity <= 0:
        print("Стоило хорошенько думать, игрок {player.name}. Игра окончена.")
        return

    # раунд 5
    print("Ты услышал звон, похожий на звон ключей")
    choice = input("Что ты сделаешь?\n1. Пойти на звон\n2. Не идти\n")
    if choice == "1":
        if player.sanity <= 20:
            print("Это были галлюцинации, ты сошёл с ума")
            player.health = 0
            player.sanity = 0
            return True
        else:
            print("Это был ключ от выхода. Скорее беги")
    elif choice == "2":
        player.health = 0
        player.sanity = 0
        return True



    print(f"Ты смог выбраться из этого места со здоровьем {player.health} и психическим состоянием {player.sanity}. Игра окончена.")
    print("Спасибо за игру!")

if __name__ == "__main__":
    play_game()